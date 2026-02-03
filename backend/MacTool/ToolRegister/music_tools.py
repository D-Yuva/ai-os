# music_tools.py
from MacTool.Tools.music import play, pause, next_track, previous_track, play_playlist, create_playlist, add_to_playlist

TOOL_REGISTRY = {
    "music_play": lambda args: play(),
    "music_pause": lambda args: pause(),
    "music_next_track": lambda args: next_track(),
    "music_previous_track": lambda args: previous_track(),
    "music_play_playlist": lambda args: play_playlist(args["name"]),
    "music_create_playlist": lambda args: create_playlist(args["name"]),
    "music_add_to_playlist": lambda args: add_to_playlist(args["file_path"], args["playlist_name"]),
}