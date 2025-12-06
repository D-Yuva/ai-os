# finder_tools.py
from MacTool.Tools.finder import create_folder, list_folder, open_path, reveal_path, move_item, copy_item, delete_item

TOOL_REGISTRY = {
    "finder_create_folder": lambda args: create_folder(args["path"]),
    "finder_list_folder": lambda args: list_folder(args["path"]),
    "finder_open": lambda args: open_path(args["path"]),
    "finder_reveal": lambda args: reveal_path(args["path"]),
    "finder_move_item": lambda args: move_item(args["source"], args["destination"]),
    "finder_copy_item": lambda args: copy_item(args["source"], args["destination"]),
    "finder_delete": lambda args: delete_item(args["path"]),
}