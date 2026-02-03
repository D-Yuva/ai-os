"""
FINDER FILESYSTEM TASKS (AppleScript-based via subprocess.run)

Supported actions:
- create_folder   : Create a new folder at a given POSIX path.
- list_folder     : List items inside a folder.
- open_path       : Open a file or folder in Finder (or default app).
- reveal_path     : Reveal a file or folder in Finder.
- move_item       : Move a file or folder to another directory.
- copy_item       : Copy a file or folder to another directory.
- delete_item     : Delete a file or folder.
"""

import os
import subprocess

def _expand(path: str) -> str:
    return os.path.expanduser(path)

def create_folder(path):
    path = _expand(path)
    parent = os.path.dirname(path)
    name = os.path.basename(path)

    if not parent or not name:
        raise ValueError(f"Invalid path: {path}")

    script = f'''
    tell application "Finder"
        if not (exists POSIX file "{parent}") then
            error "Parent folder does not exist"
        end if

        if not (exists folder "{name}" of POSIX file "{parent}") then
            make new folder at POSIX file "{parent}" with properties {{name:"{name}"}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def list_folder(path):
    path = _expand(path)
    script = f'''
    tell application "Finder"
        set itemsList to name of every item of (POSIX file "{path}" as alias)
        set AppleScript's text item delimiters to ","
        return itemsList as text
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return [x for x in result.stdout.strip().split(",") if x]

def open_path(path):
    path = _expand(path)
    script = f'''
    tell application "Finder"
        open (POSIX file "{path}" as alias)
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def reveal_path(path):
    path = _expand(path)
    script = f'''
    tell application "Finder"
        reveal (POSIX file "{path}" as alias)
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def move_item(source, destination):
    source = _expand(source)
    destination = _expand(destination)

    script = f'''
    tell application "Finder"
        move (POSIX file "{source}" as alias) to (POSIX file "{destination}" as alias) with replacing
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def copy_item(source, destination):
    source = _expand(source)
    destination = _expand(destination)

    script = f'''
    tell application "Finder"
        duplicate (POSIX file "{source}" as alias) to (POSIX file "{destination}" as alias) with replacing
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def delete_item(path):
    path = _expand(path)
    script = f'''
    tell application "Finder"
        delete (POSIX file "{path}" as alias)
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

