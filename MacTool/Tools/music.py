# music.py
import subprocess

def play():
    """Start playback in Music.app."""
    script = 'tell application "Music" to play'
    subprocess.run(["osascript", "-e", script], check=True)

def pause():
    """Pause playback in Music.app."""
    script = 'tell application "Music" to pause'
    subprocess.run(["osascript", "-e", script], check=True)

def next_track():
    """Go to the next track."""
    script = 'tell application "Music" to next track'
    subprocess.run(["osascript", "-e", script], check=True)

def previous_track():
    """Go to the previous track."""
    script = 'tell application "Music" to previous track'
    subprocess.run(["osascript", "-e", script], check=True)

def play_playlist(name):
    """
    Play a playlist with the given name.
    """
    script = f'''
    tell application "Music"
        play playlist "{name}"
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def create_playlist(name):
    """
    Create a new playlist named 'name'.
    """
    script = f'''
    tell application "Music"
        if not (exists playlist "{name}") then
            make new playlist with properties {{name:"{name}"}}
        end if
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

def add_to_playlist(file_path, playlist_name):
    """
    Add a track file to the specified playlist.
    """
    script = f'''
    tell application "Music"
        add POSIX file "{file_path}" to playlist "{playlist_name}"
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)

