from MacTool.Tools.arc import (
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

TOOL_REGISTRY = {
    "arc_open_url": lambda args: arc_open_url(args["url"]),
    "arc_search_web": lambda args: arc_search_web(args["query"]),
    "arc_google_search": lambda args: arc_google_search(args["query"]),
    "arc_new_tab": lambda args: arc_new_tab(args.get("url")),
    "arc_reload": lambda args: arc_reload(),
    "arc_back": lambda args: arc_back(),
    "arc_forward": lambda args: arc_forward(),
    "arc_close_tab": lambda args: arc_close_tab(),
    "arc_new_window": lambda args: arc_new_window(),
    "arc_find_on_page": lambda args: arc_find_on_page(args["text"]),
}