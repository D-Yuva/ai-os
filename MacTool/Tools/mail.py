# mail.py
import subprocess

def send_email(to_address, subject, content, sender=None):
    """
    Send an email via Mail.app. Requires a valid recipient (to_address).
    Optionally set sender address if needed (AppleScript format "Name <email>").
    """
    send_props = ''
    if sender:
        send_props += f'set sender to "{sender}"\n'
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{to_address}"}}
            set subject to "{subject}"
            set content to "{content}"
            {send_props}
        end tell
        send newMessage
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def create_mailbox(name):
    """
    Create a new mailbox in Mail.app with the given name (local mailbox).
    """
    script = f'''
    tell application "Mail"
        if not (exists mailbox "{name}") then
            make new mailbox with properties {{name:"{name}"}}
        end if
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def move_messages(subject, from_mailbox, to_mailbox):
    """
    Move messages with a given subject from one mailbox to another.
    """
    script = f'''
    tell application "Mail"
        set sourceBox to mailbox "{from_mailbox}"
        set destBox to mailbox "{to_mailbox}"
        set theMessages to every message of sourceBox whose subject is "{subject}"
        repeat with msg in theMessages
            move msg to destBox
        end repeat
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)