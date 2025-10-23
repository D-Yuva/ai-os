import asyncio
import subprocess
import time
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

import logging
logging.getLogger("openai.agents").setLevel(logging.ERROR)

# Notion Agent
from notion import *
from notion.search import run_search, fetch_notion_content


def create_note(title: str, content: str):
    subprocess.run(["open", "-a", "Notes"])
    time.sleep(2)
    applescript = f'''
    tell application "Notes"
        activate
        tell account "iCloud"
            tell folder "Notes"
                make new note with properties {{name:"{title}", body:"{content}"}}
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])


OLLAMA_BASE = "http://localhost:11434"

model = LitellmModel(
    model="ollama/gpt-oss:20b",
    base_url=OLLAMA_BASE,
)

notionAgent = Agent(
    name="notionAgent",
    instructions="You are an agent that fetches content from Notion. Answer all Notion-related queries as fully as possible.",
    model=model
)

macAgent = Agent(
    name="macAgent",
    instructions="You are an agent that can perform tasks on a Mac, including creating notes via system automation tools.",
    model=model
)

routerAgent = Agent(
    name="routerAgent",
    instructions="""
    You are a Router Agent. 
    For Notion-related queries, reply with 'notionAgent'.
    For any task or action needs to be done (example: open safari), reply with 'macAgent'.
    If the question is about your identity, reply 'routerAgent'.
    Otherwise, reply 'routerAgent'.
    Reply ONLY with the agent name, not with any answer.
""",
    model=model
)

async def main():
    query = "Create a note titled 'Deep Learning' explaining attention mechanisms."
    result = await Runner.run(macAgent, query)
    create_note("Deep Learning", "explaining attention mechanism")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
