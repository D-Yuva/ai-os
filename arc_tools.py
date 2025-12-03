# arc_tools.py
from agents import Tool
from arc import (
    arc_open_url,
    arc_new_tab,
    arc_search_web,
    arc_google_search,
    arc_reload,
    arc_back,
    arc_forward,
    arc_close_tab,
    arc_new_window,
    arc_find_on_page,
)

tools = [
    Tool(
        name="arc_open_url",
        description="Open a URL in the Arc browser",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to open"}
            },
            "required": ["url"],
        },
        func=lambda url: arc_open_url(url),
    ),
    Tool(
        name="arc_search_web",
        description="Search in Arc using the address bar",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"],
        },
        func=lambda query: arc_search_web(query),
    ),
    Tool(
        name="arc_new_tab",
        description="Open a new Arc tab",
        parameters={"type": "object", "properties": {}},
        func=lambda: arc_new_tab(),
    ),
    Tool(
        name="arc_reload",
        description="Reload the current Arc tab",
        parameters={"type": "object", "properties": {}},
        func=lambda: arc_reload(),
    ),
    Tool(
        name="arc_back",
        description="Navigate back in Arc browser history",
        parameters={"type": "object", "properties": {}},
        func=lambda: arc_back(),
    ),
    Tool(
        name="arc_forward",
        description="Navigate forward in Arc browser history",
        parameters={"type": "object", "properties": {}},
        func=lambda: arc_forward(),
    ),
]