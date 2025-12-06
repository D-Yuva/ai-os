# messages.py
import subprocess

def send_message(recipient, text):
    """
    Send a message via Messages.app to the given recipient (phone or email) using iMessage.
    """
    script = f'''
    tell application "Messages"
        set targetService to first service whose service type = iMessage
        send "{text}" to buddy "{recipient}" of targetService
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def list_services():
    """
    List available messaging services (e.g. iMessage, SMS).
    """
    script = '''
    tell application "Messages"
        set svcNames to name of every service
        set AppleScript's text item delimiters to ","
        return svcNames as text
    end tell'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
    return result.stdout.strip().split(",")

