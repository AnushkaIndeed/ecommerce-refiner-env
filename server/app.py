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

@app.post("/refine")
@app.post("/step")
async def refine(request: Request):
    """
    The 'step' endpoint required by the validator to submit 
    the extracted brand and receive a reward.
    """
    try:
        data = await request.json()
        field = data.get("field", "brand")
        value = data.get("value", "").upper().strip()
    
        valid_brands = ["ADIDAS", "NIKE", "PUMA", "REEBOK", "ASICS"]
        
        if value in valid_brands:
            return {
                "observation": f"Field '{field}' successfully refined to {value}",
                "reward": 1.0
            }
        else:
            return {
                "observation": f"Invalid refinement for '{field}': {value}",
                "reward": 0.0
            }
    except Exception as e:
        return {"observation": f"Error: {str(e)}", "reward": 0.0}

@app.get("/state")
async def state():
    return {"status": "active"}

# --- GRADIO UI LOGIC ---

def refine_ui_logic(text):
    """Logic for the interactive web interface."""
    prompt = f"""
    Extract attributes from the product title: {text}
    Return ONLY this format:
    BRAND: [Brand]
    COLOR: [Color]
    SIZE: [Size]
    Do not include any other text or greetings.
    """
    try:
        
        model_id = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

io = gr.Interface(
    fn=refine_ui_logic,
    inputs=gr.Textbox(label="Paste Messy Product Title", placeholder="e.g. ADIDAS ULTRABOOST BLUE 42"),
    outputs=gr.Textbox(label="Refined Result"),
    title="🛒 Ecommerce Product Refiner",
    description="Extracts structured data from messy titles using Google Gemini AI."
)


app = gr.mount_gradio_app(app, io, path="/")


def main():
    """Required by the OpenEnv validator for multi-mode deployment."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()