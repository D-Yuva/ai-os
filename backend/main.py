import os
os.environ["AGENTS_DISABLE_TELEMETRY"] = "true"

import logging
logging.getLogger("openai.agents").setLevel(logging.ERROR)

import asyncio
import litellm
import json
import re

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# Tool registries for all Mac apps
from MacTool.ToolRegister.arc_tools import TOOL_REGISTRY as ARC_TOOLS
from MacTool.ToolRegister.notes_tools import TOOL_REGISTRY as NOTES_TOOLS
from MacTool.ToolRegister.reminders_tools import TOOL_REGISTRY as REMINDERS_TOOLS
from MacTool.ToolRegister.mail_tools import TOOL_REGISTRY as MAIL_TOOLS
from MacTool.ToolRegister.keynote_tools import TOOL_REGISTRY as KEYNOTE_TOOLS
from MacTool.ToolRegister.finder_tools import TOOL_REGISTRY as FINDER_TOOLS
from MacTool.ToolRegister.music_tools import TOOL_REGISTRY as MUSIC_TOOLS
from MacTool.ToolRegister.messages_tools import TOOL_REGISTRY as MESSAGES_TOOLS
from MacTool.ToolRegister.facetime_tools import TOOL_REGISTRY as FACETIME_TOOLS

# Merge all into a single TOOL_REGISTRY used by the runtime
TOOL_REGISTRY = {}
TOOL_REGISTRY.update(ARC_TOOLS)
TOOL_REGISTRY.update(NOTES_TOOLS)
TOOL_REGISTRY.update(REMINDERS_TOOLS)
TOOL_REGISTRY.update(MAIL_TOOLS)
TOOL_REGISTRY.update(KEYNOTE_TOOLS)
TOOL_REGISTRY.update(FINDER_TOOLS)
TOOL_REGISTRY.update(MUSIC_TOOLS)
TOOL_REGISTRY.update(MESSAGES_TOOLS)
TOOL_REGISTRY.update(FACETIME_TOOLS)

# Notion Agent utilities
from notion import *
from notion.search import run_search, fetch_notion_content

litellm.disable_streaming_logging = True 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, ".agent_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def build_model(model_type: str):
    """
    Returns a model instance based on model_type
    """
    if model_type == "gemini":
        cfg = load_config()
        api_key = cfg.get("gemini_api_key")

        if not api_key:
            raise RuntimeError("Gemini API key not found")

        return LitellmModel(
            model="gemini/gemini-2.5-flash",
            api_key=api_key,
        )

    # default: ollama
    return LitellmModel(
        model="ollama/gpt-oss:20b",
        base_url=OLLAMA_BASE,
        api_key=None,
    )


OLLAMA_BASE = "http://localhost:11434"

config = load_config()
active_model = config.get("active_model", "local")
model = build_model(active_model)

def handle_model_switch():
    print("\nSelect model:")
    print("1) Local (Ollama)")
    print("2) Gemini")

    choice = input("Enter choice (1/2): ").strip()

    cfg = load_config()

    if choice == "2":
        if not cfg.get("gemini_api_key"):
            key = input("Enter Gemini API key: ").strip()
            cfg["gemini_api_key"] = key

        cfg["active_model"] = "gemini"
        save_config(cfg)
        print("✅ Switched to Gemini")

    else:
        cfg["active_model"] = "local"
        save_config(cfg)
        print("✅ Switched to Local (Ollama)")


# ---------- Sub-agents ----------

notionAgent = Agent(
    name="notionAgent",
    instructions="You are an agent that fetches content from Notion. Answer all Notion-related queries as fully as possible.",
    model=model,
)

macAgent = Agent(
    name="macAgent",
    instructions="""
    You are an agent that decides which Mac / app automation action to take.

    You do NOT execute tools yourself.
    Instead, you examine the user's request and OUTPUT A SINGLE JSON OBJECT that tells
    the Python runtime which tool to run and with what arguments.

    The Python runtime exposes these tools (by name). You must pick ONE:

    ======================
    IMPORTANT PATH RULES
    ======================
    - You DO NOT know the user's short username or home directory path.
    - NEVER guess usernames like "/Users/Shared", "/Users/yuva", etc.
    - When the user says "Desktop", "on Desktop", "under desktop", "in Desktop", etc.:
        -> ALWAYS use the path prefix "~/Desktop".
        -> Example: "Create a folder test on desktop"
           MUST become: {"path":"~/Desktop/test"} (note the tilde).
    - Prefer "~/..." paths over absolute "/Users/..." paths unless the user *explicitly*
      gives a full absolute path.
    - Do NOT use "/Users/Shared/Desktop" unless the user explicitly says that exact path.

    ======================
    ARC BROWSER TOOLS
    ======================
    1. arc_open_url
       - Purpose: Open a URL in the Arc browser.
       - Args: {"url": "<string, full URL or domain>"}

    2. arc_search_web
       - Purpose: Use Arc's address bar to search for a query.
       - Args: {"query": "<string>"}

    3. arc_google_search
       - Purpose: Open a Google search in Arc.
       - Args: {"query": "<string>"}

    4. arc_new_tab
       - Purpose: Open a new Arc tab.
       - Args: {} or {"url": "<optional URL to open in new tab>"}

    5. arc_reload
       - Purpose: Reload the current Arc tab.
       - Args: {}

    6. arc_back
       - Purpose: Go back in Arc navigation history.
       - Args: {}

    7. arc_forward
       - Purpose: Go forward in Arc navigation history.
       - Args: {}

    8. arc_close_tab
       - Purpose: Close the current Arc tab.
       - Args: {}

    9. arc_new_window
       - Purpose: Open a new Arc window.
       - Args: {}

    10. arc_find_on_page
        - Purpose: Find some text on the current Arc page (Cmd+F).
        - Args: {"text": "<string>"}


    ======================
    APPLE NOTES TOOLS
    ======================
    11. notes_create_note
        - Purpose: Create a new Apple Notes note in iCloud > Notes.
        - Args: {"title": "<string>", "content": "<string>"}

    12. notes_list_notes
        - Purpose: List all notes in iCloud > Notes.
        - Args: {}

    13. notes_read_note
        - Purpose: Read the content of a note by title.
        - Args: {"title": "<string>"}

    14. notes_delete_note
        - Purpose: Delete a note by title.
        - Args: {"title": "<string>"}

    15. notes_update_note
        - Purpose: Replace the body of a note.
        - Args: {"title": "<string>", "content": "<string>"}

    16. notes_create_folder
        - Purpose: Create a new Notes folder under iCloud.
        - Args: {"folder_name": "<string>"}

    17. notes_move_note
        - Purpose: Move a note to a different folder.
        - Args: {"title": "<string>", "folder_name": "<string>"}


    ======================
    REMINDERS TOOLS
    ======================
    When creating reminders, ALWAYS use the tool:
    "reminders_add_reminder"

    Do NOT invent tool names.
    Only use tools explicitly listed.

    18. reminders_create_list
        - Args: {"name": "<string>"}

    19. reminders_delete_list
        - Args: {"name": "<string>"}

    20. reminders_add_reminder
        - Args: {
            "list_name": "<string>",
            "title": "<string>",
            "notes": "<optional string>",
            "due_date": "<optional human-friendly date string, e.g. 'tomorrow at 5 PM' or 'next monday at 9:00 AM'>"
          }

    21. reminders_complete_reminder
        - Args: {"list_name": "<string>", "title": "<string>"}

    22. reminders_list
        - Args: {"list_name": "<string>"}

    23. reminders_delete_reminder
        - Args: {"list_name": "<string>", "title": "<string>"}


    ======================
    MAIL TOOLS
    ======================
    27. mail_send_email
        - Args: {
            "to_address": "<string>",
            "subject": "<string>",
            "content": "<string>",
            "sender": "<optional string>"
          }

    28. mail_create_mailbox
        - Args: {"name": "<string>"}

    29. mail_move_messages
        - Args: {
            "subject": "<string>",
            "from_mailbox": "<string>",
            "to_mailbox": "<string>"
          }


    ======================
    PAGES TOOLS
    ======================
    30. pages_create_document
        - Args: {"name": "<optional string>", "template": "<optional string>"}

    31. pages_open_document
        - Args: {"path": "<POSIX file path string>"}

    32. pages_close_document
        - Args: {}

    33. pages_set_text
        - Args: {"text": "<string>"}

    34. pages_export_pdf
        - Args: {"output_path": "<POSIX file path string>"}


    ======================
    KEYNOTE TOOLS
    ======================
    35. keynote_create_presentation
        - Args: {"theme": "<optional string>"}

    36. keynote_add_slide
        - Args: {}

    37. keynote_close_presentation
        - Args: {}


    ======================
    NUMBERS TOOLS
    ======================
    38. numbers_create_document
        - Args: {"name": "<optional string>"}

    39. numbers_open_document
        - Args: {"path": "<POSIX file path string>"}

    40. numbers_close_document
        - Args: {}

    41. numbers_add_sheet
        - Args: {"name": "<string>"}

    42. numbers_delete_sheet
        - Args: {"name": "<string>"}

    43. numbers_set_cell
        - Args: {
            "sheet": "<string sheet name>",
            "table": "<int table index (1-based)>",
            "cell": "<string like 'A1'>",
            "value": "<string>"
          }

    44. numbers_get_cell
        - Args: {
            "sheet": "<string sheet name>",
            "table": "<int table index (1-based)>",
            "cell": "<string like 'A1'>"
          }


    ======================
    FINDER TOOLS
    ======================
    45. finder_create_folder
        - Args: {"path": "<POSIX path string>"}

    46. finder_list_folder
        - Args: {"path": "<POSIX path string>"}

    47. finder_open
        - Args: {"path": "<POSIX path string>"}

    48. finder_reveal
        - Args: {"path": "<POSIX path string>"}

    49. finder_move_item
        - Args: {"source": "<POSIX path string>", "destination": "<POSIX path string>"}

    50. finder_copy_item
        - Args: {"source": "<POSIX path string>", "destination": "<POSIX path string>"}

    51. finder_delete
        - Args: {"path": "<POSIX path string>"}


    ======================
    MUSIC TOOLS
    ======================
    52. music_play
        - Args: {}

    53. music_pause
        - Args: {}

    54. music_next_track
        - Args: {}

    55. music_previous_track
        - Args: {}

    56. music_play_playlist
        - Args: {"name": "<string>"}

    57. music_create_playlist
        - Args: {"name": "<string>"}

    58. music_add_to_playlist
        - Args: {"file_path": "<POSIX path>", "playlist_name": "<string>"}


    ======================
    MESSAGES TOOLS
    ======================
    59. messages_send
        - Args: {"recipient": "<phone/email string>", "text": "<string>"}

    60. messages_list_services
        - Args: {}


    ======================
    FACETIME TOOLS
    ======================
    61. facetime_call
        - Args: {"number": "<phone/email string>"}


    ==========================================
    RESPONSE FORMAT (VERY IMPORTANT)
    ==========================================
    When you respond, you MUST output ONLY a single JSON object, with no backticks
    and no extra text, in this format:

    {
      "tool": "<tool_name or null>",
      "args": { ... },
      "message": "<what to tell the user after running the tool>"
    }

    Examples:

    - User: "Search in Arc for attention is all you need"
      You:
      {"tool":"arc_search_web","args":{"query":"attention is all you need"},"message":"Searching for 'attention is all you need' in Arc."}

    - User: "Open youtube.com in Arc"
      You:
      {"tool":"arc_open_url","args":{"url":"https://www.youtube.com"},"message":"Opening YouTube in Arc."}

    - User: "Create a note titled 'Deep Learning' explaining attention."
      You:
      {"tool":"notes_create_note","args":{"title":"Deep Learning","content":"Explanation of attention..."},"message":"Creating a new note 'Deep Learning' in Apple Notes."}

    - If no tool is appropriate and you only need to answer in text:
      You: {"tool": null, "args": {}, "message": "Explanation here"}

    STRICT RULES:
    - Do NOT wrap JSON in ```json or any code fences.
    - Do NOT add any extra keys.
    - Do NOT output any natural language outside the JSON.
    - Make sure the JSON is valid and parseable.
    """,
    model=model,
)

workflowAgent = Agent(
    name="workflowAgent",
    instructions="""
    You are a Workflow Planning Agent for multi-step tasks that may involve:
    - Notion (via notionAgent / Notion tools)
    - Mac automations (via macAgent and Mac tools)

    Your job:
    - Read the user's natural language request.
    - Break it into an ordered list of small, atomic steps.
    - Each step will later be executed by another agent (notionAgent or macAgent) and/or Python code.
    - You DO NOT execute tools yourself.

    You MUST respond with ONLY a single JSON object, with no backticks and no extra text:

    {
      "steps": [
        {
          "id": 1,
          "agent": "notionAgent" | "macAgent",
          "description": "<short explanation of this step>",
          "query": "<the exact prompt to send to that agent>",
          "store_as": "<optional key to store this step's textual result>"
        }
      ]
    }

    RULES:

    - Maintain a logical order.
      Example (user: "Create a new note and add Notion retrieved data into it, and also send a mail to X"):
        1) notionAgent: fetch / summarize from Notion.
        2) macAgent: create Apple Note containing that Notion content.
        3) macAgent: send an email with that same content.

    - If later steps need data from an earlier step:
      - Use "store_as" on the earlier step, e.g. "store_as": "notion_data".
      - In later steps, refer to it with a placeholder: {{notion_data}} inside the "query" string.
        The runtime will replace {{notion_data}} with the actual text result.

    - Use notionAgent for:
      - Searching / reading / summarizing content from Notion.
      - Example query: "Search my Notion for project X and give me the main points."

    - Use macAgent for:
      - Anything involving Mac tools: Notes, Mail, Finder, Arc, Reminders, etc.
      - Example query for macAgent:
        "Create an Apple Notes note titled 'Project X Summary' with the following content: {{notion_data}}"
        "Send an email to dyuva2005@gmail.com with subject 'Project X Summary' and body: {{notion_data}}"

    - Make steps as small and atomic as possible (one clear action per step).

    - NEVER output explanations or commentary, only the JSON plan.
    """,
    model=model,
)

routerAgent = Agent(
    name="routerAgent",
    instructions="""
    You are a Router Agent.

    Your job is ONLY to choose which specialist agent should handle the user's request.
    You must reply with EXACTLY ONE of these strings:
    - notionAgent
    - macAgent
    - workflowAgent
    - routerAgent

    ROUTING RULES (VERY IMPORTANT):

    1. Send to workflowAgent when:
       - The request clearly involves MULTIPLE actions or APPS, especially combinations like:
         - "Create a note and then email it..."
         - "Get data from Notion and put it into Apple Notes / Mail / Pages / etc."
         - Phrases like "and also", "then", "after that", "first ... then ...".
       - Or when both Notion and Mac automations are mentioned together.
       Examples:
         - "Create a new note and add Notion retrieved data into it and also send a mail."
         - "Fetch my meeting notes from Notion and summarize them into an Apple Notes note."

    2. Send to notionAgent when:
       - The user explicitly talks ONLY about Notion:
         - "Notion", "Notion page", "Notion database", "Notion workspace",
           "search my Notion", "update my Notion note", etc.
       - And there is no clearly separate Mac automation step.
       Examples:
         - "Search my Notion workspace for meeting notes"
         - "Get the content of my Notion page about LLMs"

    3. Send to macAgent for ANY single-step macOS / app automation, including:
       - Apple apps: Notes, Arc, Safari, Chrome, Pages, Keynote, Numbers,
         Mail, Reminders, Finder, Terminal, VS Code, etc.
       - Generic Mac actions:
         - "open", "close", "create", "type", "click", "move window",
           "take screenshot", "run AppleScript", "automate on my Mac"
       - Examples:
         - "Create a note named elon musk"
         - "List all my notes"
         - "Open Arc and search for transformers paper"
         - "Open Pages and make a new document"
         - "On my Mac, open Safari and go to youtube.com"

    4. Send to routerAgent only when:
       - The user is asking about YOU as a router:
         - "What do you do?", "Who are you?", "What is routerAgent?"

    5. If you are unsure:
       - Prefer **macAgent** by default, UNLESS the word "Notion" is clearly mentioned together with other Mac actions, in which case prefer **workflowAgent**.

    STRICT OUTPUT RULE:
    - Reply ONLY with one of: notionAgent, macAgent, workflowAgent, routerAgent
    - No extra words, no explanations, no punctuation.
    """,
    model=model,
)

# ---------- Helpers ----------

def fill_placeholders(text: str, artifacts: dict) -> str:
    """
    Replace {{key}} placeholders in 'text' with artifacts[key] if present.
    Missing keys are replaced with empty string.
    """
    if not text:
        return text

    def _repl(match):
        key = match.group(1).strip()
        return str(artifacts.get(key, ""))

    return re.sub(r"\{\{([^{}]+)\}\}", _repl, text)


async def run_mac_tool_from_query(query: str) -> str:
    mac_result = await Runner.run(macAgent, query)
    raw = (mac_result.final_output or "").strip()

    if not raw:
        return "No response from macAgent."

    data = json.loads(raw)

    tool_name = data.get("tool")
    message = data.get("message") or ""

    if tool_name is None:
        return message

    tool_func = TOOL_REGISTRY.get(tool_name)
    if not tool_func:
        return f"Unknown tool: {tool_name}"

    tool_func(data.get("args") or {})
    return message


# ---------- Routing Logic ----------
async def main(query: str) -> str:
    """
    Main entrypoint for ALL queries.
    Returns a string response suitable for UI / HTTP response.
    """

    # 1. Ask router which agent should handle this
    routing_result = await Runner.run(routerAgent, query)
    agent_name = (routing_result.final_output or "").strip().lower()

    Agents = {
        "notionagent": notionAgent,
        "macagent": macAgent,
        "workflowagent": workflowAgent,
    }

    # =====================================================
    # A. WORKFLOW MODE (QUEUE OF STEPS)
    # =====================================================
    if agent_name == "workflowagent":
        output_lines = []

        # Step 1: get the plan
        plan_result = await Runner.run(workflowAgent, query)
        raw_plan = (plan_result.final_output or "").strip()

        if not raw_plan:
            return "❌ Workflow agent returned empty plan."

        try:
            plan = json.loads(raw_plan)
        except json.JSONDecodeError as e:
            return f"❌ Workflow plan JSON error: {e}"

        steps = plan.get("steps", [])
        if not isinstance(steps, list) or not steps:
            return "❌ Workflow returned no steps."

        artifacts = {}  # stores outputs keyed by 'store_as'

        # Step 2: execute each step in order
        for step in steps:
            step_id = step.get("id")
            step_agent = (step.get("agent") or "").lower()
            step_desc = step.get("description") or ""
            step_query = step.get("query") or ""
            store_as = step.get("store_as")

            output_lines.append(f"▶ Step {step_id}: {step_desc}")

            resolved_query = fill_placeholders(step_query, artifacts)

            # ---------- Notion ----------
            if step_agent == "notionagent":
                try:
                    notion_result = run_search(resolved_query)
                    answer = notion_result.get("answer", "")
                    if store_as:
                        artifacts[store_as] = answer
                    output_lines.append(answer or "ℹ️ Notion step completed.")
                except Exception as e:
                    output_lines.append(f"❌ Notion step failed: {e}")

            # ---------- macAgent ----------
            elif step_agent == "macagent":
                try:
                    result = await run_mac_tool_from_query(resolved_query)
                    if store_as:
                        artifacts[store_as] = result
                    output_lines.append(result)
                except Exception as e:
                    output_lines.append(f"❌ Mac step failed: {e}")

            else:
                output_lines.append(f"❌ Unknown agent '{step_agent}'")

        output_lines.append("✅ Workflow complete.")
        return "\n".join(output_lines)

    # =====================================================
    # B. SIMPLE MAC MODE
    # =====================================================
    if agent_name == "macagent":
        return await run_mac_tool_from_query(query)

    # =====================================================
    # C. SIMPLE NOTION MODE
    # =====================================================
    if agent_name == "notionagent":
        try:
            result = run_search(query)
            return result.get("answer") or json.dumps(result, indent=2)
        except Exception as e:
            return f"❌ Notion error: {e}"

    # =====================================================
    # D. FALLBACK
    # =====================================================
    selected_agent = Agents.get(agent_name)
    if selected_agent:
        result = await Runner.run(selected_agent, query)
        return result.final_output or ""

    # Router talking about itself / unexpected
    return routing_result.final_output or ""



async def main_loop():
    global model, notionAgent, macAgent, workflowAgent, routerAgent

    print("Type 'exit' to quit chat.\n")

    while True:
        # ---------- SHOW ACTIVE MODEL ----------
        cfg = load_config()
        active_model = cfg.get("active_model", "local")

        print(f"/switchLLM : {active_model}")

        q = input("Enter your task (or type 'exit' to quit): ").strip()

        # ---------- EXIT ----------
        if q.lower() == "exit":
            break

        # ---------- MODEL SWITCH (CLI ONLY) ----------
        if q in {"/switch models", "/switchLLM"}:
            handle_model_switch()

            cfg = load_config()
            active_model = cfg.get("active_model", "local")

            try:
                model = build_model(active_model)
            except Exception as e:
                print(f"❌ Failed to switch model: {e}")
                continue

            # 🔁 HOT-SWAP MODEL FOR ALL AGENTS
            routerAgent.model = model
            notionAgent.model = model
            macAgent.model = model
            workflowAgent.model = model

            print(f"✅ Now using: {active_model}\n")
            continue

        # ---------- NORMAL CHAT (ALWAYS ROUTER FIRST) ----------
        try:
            await main(q)
        except Exception as e:
            print(f"❌ Runtime error: {e}")

        except Exception as e:
            print(f"❌ Runtime error: {e}")


if __name__ == "__main__":
    asyncio.run(main_loop())