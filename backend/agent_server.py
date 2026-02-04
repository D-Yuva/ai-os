from fastapi import FastAPI
from pydantic import BaseModel

# Import your main agent logic
from main import main

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/query")
async def run_agent(q: Query):
    try:
        response = await main(q.text)
        return {
            "status": "ok",
            "response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent_server:app", host="127.0.0.1", port=8000, reload=False)
