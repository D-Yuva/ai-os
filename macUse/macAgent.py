import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv

# Computer use tool - these imports are not needed for mlx_use
# from agents.tool import ComputerTool
# from agents.computer import Computer

from langchain_ollama import ChatOllama
from mlx_use import Agent
from mlx_use.controller.service import Controller

load_dotenv()  

def set_llm(llm_provider: str = None):
    if llm_provider == "ollama":
        model_name = os.getenv('OLLAMA_MODEL_NAME', 'llama3.2:latest')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            # Use ChatOllama with proper configuration for mlx_use
            return ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.1,
                top_p=0.9,
                num_ctx=4096
            )
        except Exception as e:
            print(f"Error setting up Ollama LLM: {e}")
            return None
    elif llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        if api_key:
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        else:
            raise ValueError("GEMINI_API_KEY not set in .env")
    return None

# Use Google Gemini for macOS tasks (since Ollama has compatibility issues with mlx_use)
llm = set_llm("ollama")

if not llm:
    print("Google Gemini setup failed, trying Ollama as fallback...")
    llm = set_llm("ollama")
    if not llm:
        raise ValueError("Both Gemini and Ollama LLM setup failed. Ensure your API key is correct or Ollama is running.")

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
        try:
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
        except Exception as e:
            return f"Error running macOS task: {str(e)}"

    def __call__(self, task: str, max_steps: int = 25):
        return asyncio.run(self.run(task, max_steps))
