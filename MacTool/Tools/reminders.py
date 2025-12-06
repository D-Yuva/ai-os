# reminders.py
import subprocess

def create_list(name):
    """
    Create a new Reminders list with the given name.
    """
    script = f'''
    tell application "Reminders"
        make new list with properties {{name:"{name}"}}
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def delete_list(name):
    """
    Delete the Reminders list with the given name.
    """
    script = f'''
    tell application "Reminders"
        if exists list "{name}" then delete list "{name}"
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def add_reminder(list_name, title, notes=None, due_date=None):
    """
    Add a new reminder to list 'list_name' with title. 
    Optionally set a note (body) and due date (AppleScript date string).
    """
    props = f'name:"{title}"'
    if notes:
        props += f', body:"{notes}"'
    if due_date:
        props += f', due date:date "{due_date}"'
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            make new reminder with properties {{{props}}}
        end tell
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def complete_reminder(list_name, title):
    """
    Mark the first reminder with 'title' in 'list_name' as completed.
    """
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            if exists (first reminder whose name is "{title}") then
                set completed of (first reminder whose name is "{title}") to true
            end if
        end tell
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def list_reminders(list_name):
    """
    Return names of all reminders in the given list as a string list.
    """
    script = f'''
    tell application "Reminders"
        set reminderNames to name of every reminder of list "{list_name}"
        set AppleScript's text item delimiters to ","
        return reminderNames as text
    end tell'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return result.stdout.strip().split(",")

def delete_reminder(list_name, title):
    """
    Delete the first reminder named 'title' in list 'list_name'.
    """
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            if exists (first reminder whose name is "{title}") then
                delete (first reminder whose name is "{title}")
            end if
        end tell
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)