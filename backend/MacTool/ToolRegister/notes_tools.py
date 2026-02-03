from MacTool.Tools.notes import (
    create_note,
    list_notes,
    read_note,
    delete_note,
    update_note,
    create_folder,
    move_note,
)

TOOL_REGISTRY = {
    # ---- Notes tools ----
    "notes_create_note":      lambda args: create_note(args["title"], args["content"]),
    "notes_list_notes":       lambda args: list_notes(),
    "notes_read_note":        lambda args: read_note(args["title"]),
    "notes_delete_note":      lambda args: delete_note(args["title"]),
    "notes_update_note":      lambda args: update_note(args["title"], args["content"]),
    "notes_create_folder":    lambda args: create_folder(args["folder_name"]),
    "notes_move_note":        lambda args: move_note(args["title"], args["folder_name"]),
}