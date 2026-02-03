"""
KEYNOTE PRESENTATION TASKS (AppleScript-based via subprocess.run)

Supported actions:
- keynote_create_presentation : Create a new Keynote presentation (optionally with a theme).
- keynote_add_slide           : Add a new blank slide to the front presentation.
- keynote_close_presentation  : Close the front Keynote presentation without saving.
"""

import subprocess

def create_presentation(template=None):
    """
    Create a new Keynote presentation. Optionally specify a theme name.
    """
    if template:
        script = f'''
        tell application "Keynote"
            activate
            make new document with properties {{document theme:theme "{template}"}}
        end tell'''
    else:
        script = '''
        tell application "Keynote"
            activate
            make new document
        end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def add_slide():
    """
    Add a new blank slide to the front Keynote presentation.
    """
    script = '''
    tell application "Keynote"
        if (count of documents) > 0 then
            tell front document
                make new slide at end of slides
            end tell
        end if
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def close_presentation():
    """
    Close the front Keynote document without saving.
    """
    script = '''
    tell application "Keynote"
        if (count of documents) > 0 then close front document saving no
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

