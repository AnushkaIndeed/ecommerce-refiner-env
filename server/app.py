import os
import random
import uvicorn
import gradio as gr
from fastapi import FastAPI, Request
from google import genai
from tasks import TASKS

app = FastAPI()


api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.get("/health")
async def health():
    return {"status": "online"}

@app.post("/reset")
async def reset(difficulty: str = "easy"):
    task_list = TASKS.get(difficulty, TASKS["easy"])
    selected = random.choice(task_list)
    return {"observation": selected["input"]}

@app.post("/step")
async def step(request: Request):
    try:
        data = await request.json()
        value = data.get("value", "").upper().strip()
    
        # DYNAMIC VALIDATION: Check against all brands in tasks.py
        all_brands = set()
        for diff in TASKS:
            for t in TASKS[diff]:
                brand = t.get("target", {}).get("brand", "").upper()
                if brand: all_brands.add(brand)
        
        if value in all_brands:
            return {"observation": "Success", "reward": 1.0}
        return {"observation": "Invalid Brand", "reward": 0.0}
    except Exception as e:
        return {"observation": str(e), "reward": 0.0}

# Gradio interface for manual testing
def ui_fn(text):
    model_id = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    res = client.models.generate_content(model=model_id, contents=f"Brand of: {text}")
    return res.text

io = gr.Interface(fn=ui_fn, inputs="text", outputs="text")
app = gr.mount_gradio_app(app, io, path="/")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)