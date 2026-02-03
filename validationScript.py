import asyncio
import os
import subprocess
from typing import Callable, List, Tuple

import main
from agents import Runner

# ======================================================
# GENERIC HELPERS
# ======================================================

def osascript(script: str) -> str:
    r = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def expand(path: str) -> str:
    return os.path.expanduser(path)

def app_running(app: str) -> bool:
    names = osascript(
        'tell application "System Events" to get name of every process'
    )
    return app in names

# ======================================================
# STATE VERIFIERS (MATCH TOOL IMPLEMENTATION)
# ======================================================

def folder_exists(path):
    return os.path.exists(expand(path))

def note_exists(title):
    return "true" in osascript(f'''
        tell application "Notes"
            tell account "iCloud"
                tell folder "Notes"
                    return exists note "{title}"
                end tell
            end tell
        end tell
    ''').lower()

def notes_folder_exists(name):
    return "true" in osascript(f'''
        tell application "Notes"
            tell account "iCloud"
                return exists folder "{name}"
            end tell
        end tell
    ''').lower()

def reminders_list_exists(name):
    return "true" in osascript(f'''
        tell application "Reminders"
            return exists list "{name}"
        end tell
    ''').lower()

def reminder_exists(title):
    return "true" in osascript(f'''
        tell application "Reminders"
            set found to false
            repeat with l in lists
                if exists (first reminder of l whose name is "{title}") then
                    set found to true
                    exit repeat
                end if
            end repeat
            return found
        end tell
    ''').lower()

def mailbox_exists(name):
    return "true" in osascript(f'''
        tell application "Mail"
            return exists mailbox "{name}"
        end tell
    ''').lower()

def music_playlist_exists(name):
    return "true" in osascript(f'''
        tell application "Music"
            return exists playlist "{name}"
        end tell
    ''').lower()

# ======================================================
# VALIDATION CASES (ALL TOOLS)
# ======================================================
# (tool_name, prompt, verifier, soft_pass)

VALIDATION_CASES: List[Tuple[str, str, Callable[[], bool], bool]] = [

    # ================= ARC =================
    ("arc_activation", "Activate Arc", lambda: app_running("Arc"), True),
    ("arc_focus_omnibar", "Focus the address bar in Arc", lambda: app_running("Arc"), True),
    ("arc_open_url", "Open https://example.com in Arc", lambda: app_running("Arc"), True),
    ("arc_new_tab", "Open a new tab in Arc", lambda: app_running("Arc"), True),
    ("arc_reload", "Reload the current tab in Arc", lambda: app_running("Arc"), True),
    ("arc_close_tab", "Close the current tab in Arc", lambda: app_running("Arc"), True),
    ("arc_new_window", "Open a new window in Arc", lambda: app_running("Arc"), True),
    ("arc_back", "Go back in Arc", lambda: app_running("Arc"), True),
    ("arc_forward", "Go forward in Arc", lambda: app_running("Arc"), True),
    ("arc_search_web", "Search in Arc for transformers", lambda: app_running("Arc"), True),
    ("arc_google_search", "Google search transformers in Arc", lambda: app_running("Arc"), True),
    ("arc_find_on_page", "Find text attention in Arc", lambda: app_running("Arc"), True),

    # ================= FACETIME =================
    ("facetime_call", "Call 1234567890 on FaceTime", lambda: app_running("FaceTime"), True),

    # ================= FINDER =================
    ("finder_create_folder",
     "Create a folder named ValidationFolder on Desktop",
     lambda: folder_exists("~/Desktop/ValidationFolder"), False),

    ("finder_list_folder",
     "List items in Desktop",
     lambda: True, True),

    ("finder_open",
     "Open Desktop in Finder",
     lambda: app_running("Finder"), True),

    ("finder_reveal",
     "Reveal Desktop in Finder",
     lambda: app_running("Finder"), True),

    ("finder_move_item",
     "Move ValidationFolder to Documents",
     lambda: folder_exists("~/Documents/ValidationFolder"), False),

    ("finder_copy_item",
     "Copy ValidationFolder back to Desktop",
     lambda: folder_exists("~/Desktop/ValidationFolder"), False),

    ("finder_delete",
     "Delete ValidationFolder from Desktop",
     lambda: not folder_exists("~/Desktop/ValidationFolder"), False),

    # ================= KEYNOTE =================
    ("keynote_create_presentation",
     "Create a keynote presentation",
     lambda: app_running("Keynote"), True),

    ("keynote_add_slide",
     "Add a slide to the keynote presentation",
     lambda: app_running("Keynote"), True),

    ("keynote_close_presentation",
     "Close the keynote presentation",
     lambda: True, True),

    # ================= MAIL =================
    ("mail_create_mailbox",
     "Create a mailbox named ValidationBox",
     lambda: mailbox_exists("ValidationBox"), True),

    ("mail_move_messages",
     "Move messages with subject test from Inbox to ValidationBox",
     lambda: True, True),

    ("mail_send_email",
     "Send an email to test@example.com with subject Validation",
     lambda: True, True),

    # ================= MESSAGES =================
    ("messages_list_services",
     "List message services",
     lambda: True, True),

    ("messages_send",
     "Send message hello to +1234567890",
     lambda: True, True),

    # ================= MUSIC =================
    ("music_play", "Play music", lambda: app_running("Music"), True),
    ("music_pause", "Pause music", lambda: app_running("Music"), True),
    ("music_next_track", "Next track", lambda: app_running("Music"), True),
    ("music_previous_track", "Previous track", lambda: app_running("Music"), True),

    ("music_create_playlist",
     "Create playlist ValidationPlaylist",
     lambda: music_playlist_exists("ValidationPlaylist"), False),

    ("music_play_playlist",
     "Play playlist ValidationPlaylist",
     lambda: music_playlist_exists("ValidationPlaylist"), False),

    ("music_add_to_playlist",
     "Add a song to playlist ValidationPlaylist",
     lambda: music_playlist_exists("ValidationPlaylist"), False),

    # ================= NOTES =================
    ("notes_create_note",
     "Create a note titled ValidationNote with content test",
     lambda: note_exists("ValidationNote"), False),

    ("notes_list_notes",
     "List my notes",
     lambda: True, True),

    ("notes_read_note",
     "Read the note ValidationNote",
     lambda: True, True),

    ("notes_update_note",
     "Update the note ValidationNote with content updated",
     lambda: note_exists("ValidationNote"), False),

    ("notes_create_folder",
     "Create a notes folder named ValidationFolder",
     lambda: notes_folder_exists("ValidationFolder"), False),

    ("notes_move_note",
     "Move note ValidationNote to folder ValidationFolder",
     lambda: note_exists("ValidationNote"), False),

    ("notes_delete_note",
     "Delete the note ValidationNote",
     lambda: not note_exists("ValidationNote"), False),

    # ================= REMINDERS =================
    ("reminders_create_list",
     "Create a reminders list ValidationList",
     lambda: reminders_list_exists("ValidationList"), False),

    ("reminders_add_reminder",
     "Add a reminder ValidationTask",
     lambda: reminder_exists("ValidationTask"), False),

    ("reminders_complete_reminder",
     "Complete reminder ValidationTask",
     lambda: True, True),

    ("reminders_list_reminders",
     "List reminders in ValidationList",
     lambda: True, True),

    ("reminders_delete_reminder",
     "Delete reminder ValidationTask",
     lambda: not reminder_exists("ValidationTask"), False),

    ("reminders_delete_list",
     "Delete reminders list ValidationList",
     lambda: not reminders_list_exists("ValidationList"), False),
]

# ======================================================
# VALIDATION ENGINE
# ======================================================

async def validate():
    print("\n🚀 FULL LLM TOOL VALIDATION STARTED\n")

    passed, soft, failed = [], [], []

    for tool, prompt, verifier, soft_pass in VALIDATION_CASES:
        print(f"🔍 {tool}")
        try:
            routing = await Runner.run(main.routerAgent, prompt)
            route = routing.final_output.strip().lower()

            if route not in {"macagent", "workflowagent"}:
                raise RuntimeError(f"Router selected {route}")

            await main.run_mac_tool_from_query(prompt)

            if not verifier():
                raise RuntimeError("Post-condition verification failed")

            if soft_pass:
                print("  ⚠️ SOFT PASS (environment dependent)")
                soft.append(tool)
            else:
                print("  ✅ PASS")
                passed.append(tool)

        except Exception as e:
            print("  ❌ FAIL:", e)
            failed.append((tool, str(e)))

    print("\n==============================")
    print("📊 FINAL REPORT")
    print("==============================")
    print(f"✅ Passed:     {len(passed)}")
    print(f"⚠️ Soft pass: {len(soft)}")
    print(f"❌ Failed:     {len(failed)}")

    if failed:
        print("\n❌ FAILURES:")
        for t, err in failed:
            print(f"- {t}: {err}")

# ======================================================
# ENTRYPOINT
# ======================================================

if __name__ == "__main__":
    asyncio.run(validate())