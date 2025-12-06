# keynote_tools.py
from MacTool.Tools.keynote import create_presentation, add_slide, close_presentation

TOOL_REGISTRY = {
    "keynote_create_presentation": lambda args: create_presentation(args.get("theme")),
    "keynote_add_slide": lambda args: add_slide(),
    "keynote_close_presentation": lambda args: close_presentation(),
}