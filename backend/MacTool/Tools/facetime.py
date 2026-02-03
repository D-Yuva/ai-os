"""
FACETIME TASKS (AppleScript-based via subprocess.run)

Supported actions:
- Call                  : Opens Facetime.
"""

import subprocess

def call_number(number: str):
    script = f'''
    do shell script "open facetime://{number}"
    tell application "System Events"
        tell process "FaceTime"
            set frontmost to true
            -- wait until the Call button actually exists
            repeat 10 times
                if (exists button "Call" of window 1) then exit repeat
                delay 0.5
            end repeat
            if (exists button "Call" of window 1) then
                click button "Call" of window 1
            end if
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)
