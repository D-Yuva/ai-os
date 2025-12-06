import subprocess
import time
import re

def escape_applescript_string(s: str) -> str:
    """
    Escape a Python string so it can be safely embedded inside an AppleScript
    double-quoted string literal.
    - Escapes backslashes and double quotes.
    - Converts newlines to \\n (literal backslash-n) so AppleScript stays valid.
      (Notes will show \\n; if you want real line breaks, we can do a fancier version.)
    """
    if s is None:
        return ""
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\r", "\\r")
    s = s.replace("\n", "\\n")
    return s

# -------------- Create Notes -----------------
def create_note(title: str, content: str):
    title_esc = escape_applescript_string(title)
    body_esc = escape_applescript_string(content)

    applescript = f'''
    set noteTitle to "{title_esc}"
    set noteBody to "{body_esc}"
    tell application "Notes"
        activate
        tell account "iCloud"
            tell folder "Notes"
                make new note with properties {{name:noteTitle, body:noteBody}}
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- List Notes -----------------
def list_notes():
    applescript = '''
    tell application "Notes"
        set noteNames to name of notes of folder "Notes"
        return noteNames
    end tell
    '''
    out = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True) # Capture output will save your output in the variable if not it goes to the terminal
                                                                                           # text will give the output in string instead of bytes
    notes = [name.strip() for name in out.stdout.strip().split(",") if name.strip()]
    # Format for readable output
    formatted = "\n".join([f"{i+1}. {note}" for i, note in enumerate(notes)])
    return formatted

# -------------- Read Content from notes -----------------
def read_note(title):
    applescript = f'''
    tell application "Notes"
        set n to first note of folder "Notes" whose name is "{title}"
        return body of n
    end tell
    '''
    out = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    raw = out.stdout.strip()

    # Remove HTML tags (e.g., <div>, <h1>)
    clean = re.sub(r'<.*?>', '', raw)
    # Replace known HTML entities
    clean = clean.replace('&quot', '"')
    # Replace multiple line breaks with single blank line
    clean = re.sub(r'\n+', '\n', clean)
    # Strip leading/trailing whitespace
    return clean.strip()

# -------------- Delete Note -----------------
def delete_note(title: str):
    applescript = f'''
    tell application "Notes"
        delete (first note of folder "Notes" whose name is "{title}")
    end tell
    '''
    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    result_text = result.stdout.strip()

    if result_text == "deleted":
        return f'Note "{title}" deleted'
    else:
        print(f'Failed to delete note "{title}". File Probably doesnt exist')
        print("---------------------------")
        print("Here is the list of files")
        print(list_notes())
        return "---------------------------"
        
# -------------- Update Note -----------------
def update_note(title, new_body):
    title_esc = escape_applescript_string(title)
    body_esc = escape_applescript_string(new_body)

    applescript = f'''
    tell application "Notes"
        set n to first note of folder "Notes" whose name is "{title_esc}"
        set body of n to "{body_esc}"
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Organise Note -----------------
def create_folder(folder_name):
    applescript = f'''
    tell application "Notes"
        tell account "iCloud"
            make new folder with properties {{name:"{folder_name}"}}
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Move notes between folders -----------------
def move_note(title, destination_folder):
    applescript = f'''
    tell application "Notes"
        set n to first note of folder "Notes" whose name is "{title}"
        move n to folder "{destination_folder}" of account "iCloud"
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
