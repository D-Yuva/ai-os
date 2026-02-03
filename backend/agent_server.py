from fastapi import FastAPI
from pydantic import BaseModel
from io import StringIO
import sys
import asyncio

# Import your main agent logic
from main import main

app = FastAPI()

class Query(BaseModel):
    text: str


@app.post("/query")
async def run_agent(q: Query):
    # Capture stdout so we can return the printed output
    old_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer

    try:
        await main(q.text)
    finally:
        sys.stdout = old_stdout

    output = buffer.getvalue().strip()
    return {
        "status": "ok",
        "output": output
    }


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server
    uvicorn.run("agent_server:app", host="127.0.0.1", port=8000, reload=False)
