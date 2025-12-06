# mail_tools.py
from MacTool.Tools.mail import send_email, create_mailbox, move_messages

TOOL_REGISTRY = {
    "mail_send_email": lambda args: send_email(args["to_address"], args["subject"], args["content"], args.get("sender")),
    "mail_create_mailbox": lambda args: create_mailbox(args["name"]),
    "mail_move_messages": lambda args: move_messages(args["subject"], args["from_mailbox"], args["to_mailbox"]),
}