from fastapi import FastAPI
import uvicorn
import random
from tasks import TASKS # This connects to your tasks.py file

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "online"}

@app.post("/reset")
async def reset(difficulty: str = "easy"):
    # Pick a random task from the level requested
    task_list = TASKS.get(difficulty, TASKS["easy"])
    selected = random.choice(task_list)
    return {"observation": selected["input"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)