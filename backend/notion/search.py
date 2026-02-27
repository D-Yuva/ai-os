# search.py
import os
import json
import time
import numpy as np
import hnswlib
import httpx
import ollama
from dotenv import load_dotenv, find_dotenv

# ============================================================
# ENV
# ============================================================

load_dotenv(find_dotenv(), override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

INDEX_PATH = os.path.join(ARTIFACTS_DIR, "notion_hnsw_hnswlib.index")
META_PATH  = os.path.join(ARTIFACTS_DIR, "meta.jsonl")

OLLAMA_BASE  = os.getenv("OLLAMA_BASE", "http://localhost:11435")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_EMBED_MODEL = "nomic-embed-text:latest"

OLLAMA_TIMEOUT_SEC = int(os.getenv("OLLAMA_TIMEOUT_SEC", "600"))

if not OLLAMA_MODEL:
    raise RuntimeError("Set OLLAMA_MODEL in .env (example: llama3.1:8b-instruct)")

# ============================================================
# OLLAMA CLIENT
# ============================================================

class LLMError(RuntimeError):
    pass

class OllamaClient:
    def chat(self, messages, temperature=0.2, max_tokens=800):
        url = f"{OLLAMA_BASE.rstrip('/')}/api/chat"
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(temperature),
                "num_predict": int(max_tokens)
            }
        }

        for attempt in range(3):
            try:
                with httpx.Client(timeout=OLLAMA_TIMEOUT_SEC) as client:
                    r = client.post(url, json=payload)

                if r.status_code >= 400:
                    raise LLMError(f"Ollama error {r.status_code}: {r.text}")

                data = r.json()
                msg = data.get("message", {})
                content = msg.get("content")
                if not content:
                    raise LLMError("Empty Ollama response")

                return content.strip()
            except Exception as e:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    raise LLMError(str(e))

_ollama = OllamaClient()

# ============================================================
# EMBEDDINGS
# ============================================================

def ollama_embed(text: str) -> np.ndarray:
    try:
        r = ollama.embeddings(
            model=OLLAMA_EMBED_MODEL,
            prompt=f"search_query: {text}"
        )
        return np.asarray(r["embedding"], dtype="float32")
    except Exception as e:
        raise LLMError(f"Ollama embedding failed: {e}")

# ============================================================
# LOAD INDEX + META (ONCE)
# ============================================================

_index = None
_meta  = None
_DIM   = None

def _init_index_and_meta():
    global _index, _meta, _DIM

    if _index is None:
        if not os.path.exists(INDEX_PATH):
            raise RuntimeError("Vector index not found. Run main.py first.")

        # Load meta to determine dim
        with open(META_PATH, "r", encoding="utf-8") as f:
            first = json.loads(next(f))
            _DIM = len(ollama_embed(first["text"]))

        idx = hnswlib.Index(space="cosine", dim=_DIM)
        idx.load_index(INDEX_PATH)
        idx.set_ef(256)
        _index = idx

    if _meta is None:
        metas = []
        with open(META_PATH, "r", encoding="utf-8") as f:
            for line in f:
                metas.append(json.loads(line))
        _meta = metas

    return _index, _meta

# ============================================================
# RANKING UTILITIES
# ============================================================

def recency_weight(created_at: float) -> float:
    """
    Bias towards newer chunks.
    7 days → full weight
    Older → gradual decay
    """
    age = time.time() - created_at
    days = age / 86400
    return max(0.4, 1.2 - (days / 7))

def score_chunk(dist, meta):
    if not meta.get("active", True):
        return None

    freshness = recency_weight(meta.get("created_at", time.time()))
    similarity = 1.0 - dist
    return similarity * freshness

# ============================================================
# ANSWER GENERATION
# ============================================================

def generate_answer(query: str, context: str) -> str:
    system = (
        "You are a helpful assistant.\n"
        "Answer ONLY using the provided context.\n"
        "If the answer is not present, say \"I don't know.\".\n"
        "Be concise and factual.\n"
        "Do not hallucinate."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Question:\n{query}\n\nContext:\n{context}"}
    ]

    return _ollama.chat(messages, temperature=0.2, max_tokens=800)

# ============================================================
# CORE SEARCH FUNCTION
# ============================================================

def fetch_notion_content(query: str, top_k: int = 8) -> dict:
    """
    Used by agents.
    Returns:
      {
        "answer": str,
        "sources": [{"chunk_idx": int, "url": str}]
      }
    """
    index, metas = _init_index_and_meta()

    qvec = ollama_embed(query)
    labels, dists = index.knn_query(qvec, k=50)

    scored = []
    for idx, dist in zip(labels[0], dists[0]):
        meta = metas[int(idx)]
        s = score_chunk(dist, meta)
        if s is not None:
            scored.append((s, idx, meta))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    if not top:
        return {"answer": "I don't know.", "sources": []}

    context_parts = []
    sources = []

    for i, (_, idx, meta) in enumerate(top, start=1):
        header = f"[S{i}] {meta.get('url','')}"
        body = meta.get("text", "").replace("\n", " ").strip()
        if not body:
            continue
        context_parts.append(header + "\n" + body)
        sources.append({
            "chunk_idx": idx,
            "url": meta.get("url", "")
        })

    context = "\n\n".join(context_parts)
    answer = generate_answer(query, context)

    return {"answer": answer, "sources": sources}

# ============================================================
# PUBLIC ENTRYPOINT (FOR AGENTS)
# ============================================================

def run_search(query: str) -> dict:
    result = fetch_notion_content(query)

    print("\n=== Answer ===")
    print(result["answer"])
    print("\n=== Sources ===")
    for s in result["sources"]:
        print(f"- chunk #{s['chunk_idx']} → {s['url']}")

    return result

# ============================================================
# CLI MODE (OPTIONAL)
# ============================================================

if __name__ == "__main__":
    try:
        while True:
            q = input("\nQuery: ").strip()
            if not q:
                break
            run_search(q)
    except KeyboardInterrupt:
        pass
