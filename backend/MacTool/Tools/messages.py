"""
MESSAGES.APP TASKS (AppleScript-based via subprocess.run)

Supported actions:
- messages_send_message   : Send an iMessage to a recipient (phone or email).
- messages_list_services  : List available messaging services (e.g. iMessage, SMS).
"""

import subprocess

import subprocess

def send_message(recipient, text):
    script = f'''
    tell application "Messages"
        set svc to first service whose service type = iMessage
        send "{text}" to buddy "{recipient}" of svc
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def list_services():
    script = '''
    tell application "Messages"
        set names to name of every service
        set AppleScript's text item delimiters to ","
        return names as text
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [x for x in result.stdout.strip().split(",") if x]
