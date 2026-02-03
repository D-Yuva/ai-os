"""
REMINDERS.APP TASKS (AppleScript-based via subprocess.run)

Supported actions:
- reminders_create_list      : Create a new reminders list.
- reminders_delete_list      : Delete an existing reminders list.
- reminders_add_reminder     : Add a reminder to a list (with notes and due date).
- reminders_complete_reminder: Mark a reminder as completed.
- reminders_list_reminders   : List all reminders in a given list.
- reminders_delete_reminder  : Delete a reminder from a list.
"""

import subprocess

def create_list(name):
    script = f'''
    tell application "Reminders"
        if not (exists list "{name}") then
            make new list with properties {{name:"{name}"}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def delete_list(name):
    script = f'''
    tell application "Reminders"
        if exists list "{name}" then delete list "{name}"
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def add_reminder(list_name, title, notes=None, due_date=None):
    props = f'name:"{title}"'
    if notes:
        props += f', body:"{notes}"'
    if due_date:
        props += f', due date:date "{due_date}"'

    script = f'''
    tell application "Reminders"
        if exists list "{list_name}" then
            tell list "{list_name}" to make new reminder with properties {{{props}}}
        else
            tell first list to make new reminder with properties {{{props}}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def complete_reminder(list_name, title):
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            set r to first reminder whose name is "{title}"
            set completed of r to true
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def list_reminders(list_name):
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            set names to name of reminders
            set AppleScript's text item delimiters to ","
            return names as text
        end tell
    end tell
    '''
    out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return [x for x in out.stdout.strip().split(",") if x]

def delete_reminder(list_name, title):
    script = f'''
    tell application "Reminders"
        tell list "{list_name}"
            delete (first reminder whose name is "{title}")
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)
