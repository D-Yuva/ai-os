# messages_tools.py
from MacTool.Tools.messages import send_message, list_services

TOOL_REGISTRY = {
    "messages_send": lambda args: send_message(args["recipient"], args["text"]),
    "messages_list_services": lambda args: list_services(),
}