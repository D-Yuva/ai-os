# MacTool/ToolRegister/reminders_tools.py

# reminders_tools.py
from MacTool.Tools.reminders import create_list, delete_list, add_reminder, complete_reminder, list_reminders, delete_reminder

TOOL_REGISTRY = {
    "reminders_create_list": lambda args: create_list(args["name"]),
    "reminders_delete_list": lambda args: delete_list(args["name"]),
    "reminders_add_reminder": lambda args: add_reminder(
        args["list_name"],
        args["title"],
        args.get("notes"),
        args.get("due_date")
    ),
    "reminders_complete_reminder": lambda args: complete_reminder(args["list_name"], args["title"]),
    "reminders_list": lambda args: list_reminders(args["list_name"]),
    "reminders_delete_reminder": lambda args: delete_reminder(args["list_name"], args["title"]),
}

# 👇 ADD THIS
TOOL_REGISTRY["reminders_create_reminder"] = TOOL_REGISTRY["reminders_add_reminder"]