"""
NOTES.APP TASKS (AppleScript-based via subprocess.run)

Supported actions:
- notes_create_note        : Create a new note with a title and content.
- notes_list_notes         : List all notes in the default Notes folder.
- notes_read_note          : Read the content of a note by title.
- notes_delete_note        : Delete a note by title.
- notes_update_note        : Update the body of an existing note.
- notes_create_folder      : Create a new folder in Notes (iCloud).
- notes_move_note          : Move a note to another folder.
"""

import subprocess
import re

def _esc(s):
    """
    Escape a Python string so it can be safely embedded inside an AppleScript
    double-quoted string literal.
    - Escapes backslashes and double quotes.
    - Converts newlines to \\n (literal backslash-n) so AppleScript stays valid.
      (Notes will show \\n; if you want real line breaks, we can do a fancier version.)
    """
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

def create_note(title, content):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                make new note with properties {{name:"{_esc(title)}", body:"{_esc(content)}"}}
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def list_notes():
    script = '''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                set names to name of notes
                return names
            end tell
        end tell
    end tell
    '''
    out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return [x.strip() for x in out.stdout.split(",") if x.strip()]

def read_note(title):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                set n to first note whose name is "{_esc(title)}"
                return body of n
            end tell
        end tell
    end tell
    '''
    out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return re.sub(r'<.*?>', '', out.stdout).strip()

def update_note(title, body):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                set n to first note whose name is "{_esc(title)}"
                set body of n to "{_esc(body)}"
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def delete_note(title):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                delete (first note whose name is "{_esc(title)}")
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def create_folder(folder):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            if not (exists folder "{folder}") then
                make new folder with properties {{name:"{folder}"}}
            end if
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def move_note(title, folder):
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            set n to first note of folder "Notes" whose name is "{_esc(title)}"
            move n to folder "{folder}"
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)
