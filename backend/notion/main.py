import os
import time
import json
import threading
import sqlite3
import hashlib
import numpy as np
import httpx
import hnswlib
import ollama

from dotenv import load_dotenv
from tqdm import tqdm
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError
from httpx import RemoteProtocolError
from datetime import datetime
from notion_client.errors import HTTPResponseError

# ============================================================
# ENV + CLIENTS
# ============================================================

load_dotenv()

ARTIFACTS_DIR = "artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

STATE_PATH = os.path.join(ARTIFACTS_DIR, "state.json")
BLOCK_DB_PATH = os.path.join(ARTIFACTS_DIR, "blocks.db")
META_PATH = os.path.join(ARTIFACTS_DIR, "meta.jsonl")
HNSW_INDEX_PATH = os.path.join(ARTIFACTS_DIR, "notion_hnsw_hnswlib.index")
PAGE_CKPT_PATH = os.path.join(ARTIFACTS_DIR, "page_checkpoint.json")

OLLAMA_EMBED_MODEL = "qllama/bge-small-en-v1.5"
OLLAMA_HOST = "http://127.0.0.1:11435"

httpx_client = httpx.Client(
    timeout=httpx.Timeout(100.0, connect=15.0)
)

notion = Client(
    auth=os.getenv("NOTION_TOKEN"),
    client=httpx_client
)

ollama_client = ollama.Client(
    host=OLLAMA_HOST,
    timeout=120
)

# ============================================================
# STATE + CHECKPOINTS
# ============================================================

def load_state():
    if not os.path.exists(STATE_PATH):
        return {"last_sync_time": 0}
    try:
        with open(STATE_PATH, "r") as f:
            data = f.read().strip()
            if not data:
                return {"last_sync_time": 0}
            return json.loads(data)
    except Exception:
        return {"last_sync_time": 0}

def save_state(state):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)

def load_page_checkpoint():
    if not os.path.exists(PAGE_CKPT_PATH):
        return set()
    with open(PAGE_CKPT_PATH, "r") as f:
        return set(json.load(f))

def save_page_checkpoint(done_pages):
    with open(PAGE_CKPT_PATH, "w") as f:
        json.dump(list(done_pages), f)

# ============================================================
# BLOCK HASH DB
# ============================================================

def init_block_db():
    conn = sqlite3.connect(BLOCK_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            block_id TEXT PRIMARY KEY,
            page_id TEXT,
            content_hash TEXT,
            last_indexed REAL
        )
    """)
    conn.commit()
    conn.close()

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def block_changed(block_id: str, text: str) -> bool:
    h = hash_text(text)
    conn = sqlite3.connect(BLOCK_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content_hash FROM blocks WHERE block_id=?", (block_id,))
    row = cur.fetchone()
    conn.close()
    return row is None or row[0] != h

def update_block(block_id: str, page_id: str, text: str):
    h = hash_text(text)
    conn = sqlite3.connect(BLOCK_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO blocks
        (block_id, page_id, content_hash, last_indexed)
        VALUES (?, ?, ?, ?)
    """, (block_id, page_id, h, time.time()))
    conn.commit()
    conn.close()

# ============================================================
# NOTION HELPERS
# ============================================================

def notion_time_to_epoch(ts: str) -> float:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0

def all_pages(max_retries=5):
    pages = {}
    cursor = None

    while True:
        for attempt in range(max_retries):
            try:
                resp = notion.search(
                    **({"start_cursor": cursor} if cursor else {}),
                    filter={"property": "object", "value": "page"}
                )
                break
            except (httpx.RemoteProtocolError, RemoteProtocolError) as e:
                wait = 2 ** attempt
                print(f"[RAG][WARN] search connection dropped, retrying in {wait}s")
                time.sleep(wait)
            except HTTPResponseError as e:
                status = getattr(e.response, "status_code", None)
                if status in (502, 503, 504) and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"[RAG][WARN] Notion {status} on search, retrying in {wait}s")
                    time.sleep(wait)
                else:
                    raise
        else:
            raise RuntimeError("[RAG] Notion search failed after retries")

        for p in resp.get("results", []):
            pages[p["id"]] = p

        if not resp.get("has_more"):
            break

        cursor = resp.get("next_cursor")
        time.sleep(0.2)  # gentle pacing

    return list(pages.values())

def plain(rt):
    if rt is None:
        return ""
    if isinstance(rt, str):
        return rt
    if isinstance(rt, list):
        return "".join(
            t.get("plain_text", str(t)) if isinstance(t, dict) else str(t)
            for t in rt
        )
    return str(rt)

# ============================================================
# SAFE BLOCK FLATTENER (CRITICAL FIX)
# ============================================================

def flatten_blocks(block_id, max_depth=6, max_blocks=500, max_seconds=30):
    out = []
    start_time = time.time()
    visited = 0

    def fetch_children(bid, cursor=None, retries=3):
        for attempt in range(retries):
            try:
                return notion.blocks.children.list(block_id=bid, start_cursor=cursor)
            except HTTPResponseError as e:
                status = getattr(e.response, "status_code", None)
                if status in (502, 503, 504) and attempt < retries - 1:
                    wait = 2 ** attempt
                    print(f"[RAG][WARN] Notion {status} on {bid}, retrying in {wait}s")
                    time.sleep(wait)
                    continue
                print(f"[RAG][WARN] Notion error {status} on {bid}, skipping block")
                return None
            except (APIResponseError, RequestTimeoutError, RemoteProtocolError) as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    print(f"[RAG][WARN] Network error on {bid}, retrying in {wait}s")
                    time.sleep(wait)
                    continue
                print(f"[RAG][WARN] Network failure on {bid}, skipping block")
                return None

        return None

    def walk(bid, depth):
        nonlocal visited

        if depth > max_depth:
            return
        if time.time() - start_time > max_seconds:
            print(f"[RAG][WARN] flatten timeout on page {block_id}")
            return

        cursor = None
        while True:
            resp = fetch_children(bid, cursor)
            if resp is None:
                return  # skip this branch safely

            for b in resp.get("results", []):
                visited += 1
                if visited > max_blocks:
                    print(f"[RAG][WARN] block limit hit on page {block_id}")
                    return

                t = b.get("type")
                if t and isinstance(b.get(t), dict):
                    obj = b[t]
                    if "rich_text" in obj:
                        text = plain(obj["rich_text"])
                        if text.strip():
                            out.append((b["id"], text))
                    if "title" in obj:
                        text = plain(obj["title"])
                        if text.strip():
                            out.append((b["id"], text))

                if b.get("has_children"):
                    walk(b["id"], depth + 1)

            if not resp.get("has_more"):
                break
            cursor = resp["next_cursor"]
            time.sleep(0.1)

    walk(block_id, 0)
    return out

# ============================================================
# CHUNKING
# ============================================================

def chunk_words(text, size=450, overlap=60):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks

# ============================================================
# EMBEDDING
# ============================================================

def embed_with_ollama(text, retries=3):
    for i in range(retries):
        try:
            r = ollama_client.embeddings(
                model=OLLAMA_EMBED_MODEL,
                prompt=f"search_document: {text}"
            )
            return r["embedding"]
        except Exception:
            time.sleep(2 ** i)
    return None

def embed_chunks(chunks):
    vecs = []
    for ch in tqdm(chunks, desc="Embedding chunks", unit="chunk"):
        emb = embed_with_ollama(ch)
        if emb is not None:
            vecs.append(emb)
    return np.asarray(vecs, dtype="float32")

# ============================================================
# HNSW
# ============================================================

def load_or_create_index(dim):
    if os.path.exists(HNSW_INDEX_PATH):
        idx = hnswlib.Index(space="cosine", dim=dim)
        idx.load_index(HNSW_INDEX_PATH)
        idx.set_ef(256)
        return idx
    idx = hnswlib.Index(space="cosine", dim=dim)
    idx.init_index(max_elements=1_000_000, ef_construction=200, M=32)
    idx.set_ef(256)
    return idx

# ============================================================
# INDEXING
# ============================================================

def incremental_index_page(page):
    print("   ↳ flattening")
    blocks = flatten_blocks(page["id"])

    if not blocks:
        print("   ↳ no blocks")
        return

    print(f"   ↳ blocks: {len(blocks)}")

    new_chunks = []
    new_meta = []

    print("   ↳ chunking")
    for block_id, text in blocks:
        if not block_changed(block_id, text):
            continue

        chunks = chunk_words(text)
        for ch in chunks:
            new_chunks.append(ch)
            new_meta.append({
                "page_id": page["id"],
                "url": page.get("url", ""),
                "block_id": block_id,
                "text": ch,
                "created_at": time.time(),
                "active": True
            })

        update_block(block_id, page["id"], text)

    if not new_chunks:
        print("   ↳ no new chunks")
        return

    print(f"   ↳ embedding {len(new_chunks)} chunks")
    vecs = embed_chunks(new_chunks)

    print("   ↳ updating index")
    idx = load_or_create_index(vecs.shape[1])
    start = idx.get_current_count()
    ids = np.arange(start, start + vecs.shape[0])
    idx.add_items(vecs, ids)
    idx.save_index(HNSW_INDEX_PATH)

    with open(META_PATH, "a", encoding="utf-8") as f:
        for m in new_meta:
            f.write(json.dumps(m) + "\n")

    print("   ↳ page complete")

# ============================================================
# BOOTSTRAP + DAEMON
# ============================================================

def bootstrap_full_index():
    print("[RAG] Bootstrap indexing started")

    init_block_db()
    pages = all_pages()
    done_pages = load_page_checkpoint()

    print(f"[RAG] Total pages: {len(pages)}")
    print(f"[RAG] Already done: {len(done_pages)}")

    for i, p in enumerate(pages, start=1):
        pid = p["id"]
        if pid in done_pages:
            continue

        print(f"[RAG] ({i}/{len(pages)}) Page {pid}")
        try:
            incremental_index_page(p)
            done_pages.add(pid)
            save_page_checkpoint(done_pages)
        except Exception as e:
            print(f"[RAG][ERROR] page failed {pid}: {e}")

    save_state({"last_sync_time": time.time()})
    print("[RAG] Bootstrap indexing completed")

def notion_sync_daemon():
    state = load_state()
    while True:
        try:
            pages = all_pages()
            for p in pages:
                last_edit = p.get("last_edited_time")
                if last_edit and notion_time_to_epoch(last_edit) > state["last_sync_time"]:
                    incremental_index_page(p)

            state["last_sync_time"] = time.time()
            save_state(state)
        except Exception as e:
            print("[RAG daemon error]", e)

        time.sleep(600)

# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    print("🚀 ai-os RAG daemon starting...")
    bootstrap_full_index()
    threading.Thread(target=notion_sync_daemon, daemon=True).start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down.")
