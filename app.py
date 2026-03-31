from fastapi import FastAPI, Request
import uvicorn
import random
from tasks import TASKS 

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "online"}

@app.post("/reset")
async def reset(difficulty: str = "easy"):
    task_list = TASKS.get(difficulty, TASKS["easy"])
    selected = random.choice(task_list)
    return {"observation": selected["input"]}

# This is the missing piece! 
# It handles BOTH common endpoint names used in the hackathon.
@app.post("/refine")
@app.post("/step")
async def refine(request: Request):
    data = await request.json()
    # Your agent sends 'field' and 'value'
    field = data.get("field")
    value = data.get("value", "").upper().strip()
    
    # Simple validation logic for the brand
    if value in ["ADIDAS", "NIKE", "PUMA"]:
        return {
            "observation": f"Brand successfully refined to {value}",
            "reward": 1.0
        }
    else:
        return {
            "observation": f"Invalid brand or refinement failed: {value}",
            "reward": 0.0
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)