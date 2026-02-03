"""
MAIL.APP TASKS (AppleScript-based via subprocess.run)

Supported actions:
- mail_send_email      : Send an email via Mail.app.
- mail_create_mailbox  : Create a new local mailbox in Mail.app.
- mail_move_messages   : Move emails between mailboxes based on subject.
"""

import subprocess

def send_email(to_address, subject, content, sender=None):
    sender_line = f'set sender to "{sender}"' if sender else ""

    script = f'''
    tell application "Mail"
        set msg to make new outgoing message with properties {{visible:false, subject:"{subject}", content:"{content}"}}
        tell msg
            make new to recipient at end of to recipients with properties {{address:"{to_address}"}}
            {sender_line}
        end tell
        send msg
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def create_mailbox(name):
    script = f'''
    tell application "Mail"
        if not (exists mailbox "{name}") then
            make new mailbox with properties {{name:"{name}"}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def move_messages(subject, from_mailbox, to_mailbox):
    script = f'''
    tell application "Mail"
        if not (exists mailbox "{from_mailbox}") then error "Source mailbox missing"
        if not (exists mailbox "{to_mailbox}") then error "Destination mailbox missing"

        set src to mailbox "{from_mailbox}"
        set dst to mailbox "{to_mailbox}"

        set msgs to every message of src whose subject is "{subject}"
        repeat with m in msgs
            move m to dst
        end repeat
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)