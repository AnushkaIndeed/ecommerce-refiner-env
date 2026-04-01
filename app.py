from fastapi import FastAPI, Request
import uvicorn
import random
import gradio as gr
from tasks import TASKS 
import os
from google import genai
app = FastAPI()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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

def refine_ui_logic(text):
    prompt = f"""
Extract attributes from: {text}
Return ONLY this format:
BRAND: [Brand]
COLOR: [Color]
SIZE: [Size]
Do not include any other text or greetings.
"""
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# Create the Gradio Interface
io = gr.Interface(
    fn=refine_ui_logic,
    inputs=gr.Textbox(label="Paste Messy Product Title", placeholder="e.g. ADIDAS ULTRABOOST BLUE 42"),
    outputs=gr.Textbox(label="Refined Result"),
    title="🛒 Ecommerce Product Refiner",
    description="Extracts structured data from messy titles using AI."
)

# Mount Gradio onto the FastAPI app at the root ("/")
app = gr.mount_gradio_app(app, io, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)