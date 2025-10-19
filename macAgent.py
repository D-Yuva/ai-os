import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv

#Computer use tool
from agents.tool import ComputerTool
from agents.computer import Computer

from langchain_google_genai import ChatGoogleGenerativeAI
from mlx_use import Agent
from mlx_use.controller.service import Controller

load_dotenv()  

def set_llm(llm_provider: str = None):
    if llm_provider == "google":
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        if api_key:
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        else:
            raise ValueError("GEMINI_API_KEY not set in .env")
    return None

llm = set_llm("google")

if not llm:
    raise ValueError("Gemini LLM setup failed. Ensure your API key is correct and .env is loaded.")

controller = Controller()

# mlx_tool.py

import asyncio
from mlx_use import Agent as MlxAgent

class MlxAgentTool:
    def __init__(self, llm, controller, name="mlx_agent_tool"):
        self.llm = llm
        self.controller = controller
        self.name = name 

    async def run(self, task: str, max_steps: int = 25):
        mlx_agent = MlxAgent(
            task=task,
            llm=self.llm,
            controller=self.controller,
            use_vision=False,
            max_actions_per_step=4,
            max_failures=5
        )
        await mlx_agent.run(max_steps=max_steps)
        return "mlx task complete"

    def __call__(self, task: str, max_steps: int = 25):
        return asyncio.run(self.run(task, max_steps))
