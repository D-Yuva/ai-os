# facetime_tools.py
from MacTool.Tools.facetime import call_number

TOOL_REGISTRY = {
    "facetime_call": lambda args: call_number(args["number"]),
}