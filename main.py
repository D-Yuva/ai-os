import os
os.environ["AGENTS_DISABLE_TELEMETRY"] = "true"

import logging
logging.getLogger("openai.agents").setLevel(logging.ERROR)

# MacOS-Use
from macAgent import MlxAgentTool
from macAgent import llm, controller
mlx_tool = MlxAgentTool(llm, controller)

# Notion Agent
from notion import *
from notion.search import run_search, fetch_notion_content

from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner
import asyncio
import os

OLLAMA_BASE = "http://localhost:11434"

model = LitellmModel(
    model="ollama/gpt-oss:20b",
    base_url=OLLAMA_BASE,
    api_key=None,
)

# Sub-agents
notionAgent = Agent(
    name="notionAgent",
    instructions="You are an agent that fetches content from Notion. Answer all Notion-related queries as fully as possible.",
    model=model
)

macAgent = Agent(
    name="macAgent",
    instructions="You are an agent that can perform tasks on a Mac system using Python code. Handle all Mac automation, scripting, and troubleshooting queries.",
    model=model,
    tools=[mlx_tool]

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

async def main(query):
    # First, get routing decision as agent name string
    routing_result = await Runner.run(routerAgent, query)
    agent_name = (routing_result.final_output or "").strip().lower()
    
    Agents = {
        "notionagent": notionAgent,
        "macagent": macAgent,
    }
    # Route based on agent name
    if agent_name == "macagent":
        result = await mlx_tool.run(query)
    elif agent_name == "notionagent":
        result = run_search(query)
    elif agent_name in Agents:
        selected_agent = Agents[agent_name]
        result = await Runner.run(selected_agent, query)
        print(f"{result.last_agent.name}: {result.final_output}")
    else:
        result = routing_result  # Fallback to routerAgent's response
        print(f"{result.last_agent.name}: {result.final_output}")
    

if __name__ == "__main__":
    print("Type 'exit' to quit chat.")
    while True:
        query = input("Enter your task (or type 'exit' to quit): ")
        if query.strip().lower() == "exit":
            break
        asyncio.run(main(query))
