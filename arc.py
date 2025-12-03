import subprocess
import time
import urllib.parse
import asyncio

def arc_activation():
    applescript = 'tell application "Arc" to activate'
    subprocess.run(["osascript", "-e", applescript])
"""
ARC: BASIC FUNCTIONS
"""

# -------------- Open Arc's address bar -----------------
def arc_focus_omnibar():
    applescript = '''
    tell application "Arc" to activate   
    tell application "System Events"
        keystroke "l" using {command down}  
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Open the url -----------------
# With the help of the user's browser history the url must be retrived. 
# Can vectorise the browser data to get this done
def arc_open_url(url: str=None):
    subprocess.run(["open", "-a", "Arc", url])

# -------------- Opens a new tab -----------------
def arc_new_tab(url: str=None):
    if url:
        arc_open_url()
        return 
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events"
        keystroke "t" using {command down}
    end tell
    '''
    subprocess.run(["osascript", '-e', applescript])

"""
ARC: BASIC NAVIGATION
"""
# -------------- Reloads the tab -----------------
def arc_reload():
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events" to keystroke "r" using {command down}
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- closes the tab -----------------
def arc_close_tab():
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events" to keystroke "w" using {command down}
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Opens new Window -----------------
def arc_new_window():
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events" to keystroke "n" using {command down, shift down}
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Go Back / Forward -----------------
def arc_back():
    """
    Navigate back in history (Cmd + [).
    """
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events"
        keystroke "[" using {command down}
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

def arc_forward():
    """
    Navigate forward in history (Cmd + ]).
    """
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events"
        keystroke "]" using {command down}
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

"""
ARC: SEARCH / FIND
"""

# -------------- Search the web via Arc's address bar -----------------
def arc_search_web(query: str):
    """
    Use Arc's address bar to search the web for a query.
    This simulates:
      - Cmd + L to focus omnibar
      - typing the query
      - pressing Return
    """
    escaped = query.replace('"', '\\"')  # escape quotes for AppleScript

    applescript = f'''
    tell application "Arc" to activate
    delay 0.1
    tell application "System Events"
        keystroke "l" using {{command down}}
        delay 0.1
        keystroke "{escaped}"
        delay 0.1
        key code 36 -- Return
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Google search using URL (alternative) -----------------
def arc_google_search(query: str):
    """
    Open a Google search for the query in Arc using a URL.
    """
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    arc_open_url(url)

# -------------- Find on page -----------------
def arc_find_on_page(text: str):
    """
    Find text on the current page (Cmd + F) and type the query.
    """
    escaped = text.replace('"', '\\"')

    applescript = f'''
    tell application "Arc" to activate
    delay 0.1
    tell application "System Events"
        keystroke "f" using {{command down}}
        delay 0.1
        keystroke "{escaped}"
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

# -------------- Find next / previous match -----------------
def arc_find_next():
    """
    Jump to the next find result (Enter in find box – approximated by Cmd + G).
    """
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events"
        keystroke "g" using {command down}
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

def arc_find_previous():
    """
    Jump to the previous find result (Shift + Cmd + G).
    """
    applescript = '''
    tell application "Arc" to activate
    tell application "System Events"
        keystroke "g" using {command down, shift down}
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])