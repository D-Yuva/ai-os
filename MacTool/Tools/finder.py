# finder.py
import os
import subprocess

def create_folder(path):
    """
    Create a new folder at the specified POSIX path.
    `path` is the full path including the new folder name,
    e.g. "~/Desktop/Test".
    """
    # Expand ~ and normalise
    expanded_path = os.path.expanduser(path)
    parent_dir = os.path.dirname(expanded_path)
    folder_name = os.path.basename(expanded_path)

    # Safety: if somehow parent_dir is empty, fall back to expanded_path's dirname
    if not parent_dir:
        raise ValueError(f"Invalid path for folder creation: {path}")

    script = f'''
    tell application "Finder"
        -- Make sure the parent folder exists
        if not (exists POSIX file "{parent_dir}") then
            error "Parent folder does not exist: {parent_dir}"
        end if

        -- Only create if it doesn't already exist
        if not (exists folder "{folder_name}" of POSIX file "{parent_dir}") then
            make new folder at POSIX file "{parent_dir}" with properties {{name:"{folder_name}"}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def list_folder(path):
    """
    List names of items in the folder at path.
    """
    script = f'''
    tell application "Finder"
        set theItems to name of every item of (POSIX file "{path}" as alias)
        set AppleScript's text item delimiters to ","
        return theItems as text
    end tell'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return result.stdout.strip().split(",")

def open_path(path):
    """
    Open the given file or folder in Finder (or appropriate application).
    """
    script = f'''
    tell application "Finder" to open POSIX file "{path}"
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def reveal_path(path):
    """
    Reveal the file or folder at path in a Finder window.
    """
    script = f'''
    tell application "Finder" to reveal (POSIX file "{path}" as alias)
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def move_item(source, destination):
    """
    Move a file or folder (POSIX paths) to destination (folder).
    """
    script = f'''
    tell application "Finder"
        move (POSIX file "{source}" as alias) to (POSIX file "{destination}" as alias) with replacing
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def copy_item(source, destination):
    """
    Copy a file or folder to the destination folder.
    """
    script = f'''
    tell application "Finder"
        duplicate (POSIX file "{source}" as alias) to (POSIX file "{destination}" as alias) with replacing
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def delete_item(path):
    """
    Delete a file or folder at the given path.
    """
    script = f'''
    tell application "Finder"
        delete (POSIX file "{path}" as alias)
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

