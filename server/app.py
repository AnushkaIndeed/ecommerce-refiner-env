import os
import random
import uvicorn
import gradio as gr
from fastapi import FastAPI, Request
from google import genai

# Relative import for the tasks file
try:
    from tasks import TASKS
except ImportError:
    from server.tasks import TASKS

app = FastAPI()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.get("/health")
async def health(): return {"status": "online"}

@app.post("/reset")
async def reset():
    all_tasks = TASKS["easy"] + TASKS["medium"] + TASKS["hard"]
    selected = random.choice(all_tasks)
    return {"observation": selected["input"]}

@app.post("/step")
async def step(request: Request):
    data = await request.json()
    val = data.get("value", "").upper().strip()
    
    # Dynamic Validation: Ensures reward=1.0 for any brand in tasks.py
    valid_brands = set()
    for diff in TASKS:
        for t in TASKS[diff]:
            valid_brands.add(t["target"]["brand"].upper())
            
    reward = 1.0 if val in valid_brands else 0.0
    return {"reward": reward}

# Professional UI
def ui_fn(text):
    res = client.models.generate_content(model="gemini-2.5-flash", contents=f"Extract brand from: {text}")
    return res.text

io = gr.Interface(fn=ui_fn, inputs="text", outputs="text", title="Ecommerce Refiner")
app = gr.mount_gradio_app(app, io, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)