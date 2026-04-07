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

@app.post("/refine")
@app.post("/step")
async def refine(request: Request):
    data = await request.json()
    field = data.get("field", "brand")
    value = data.get("value", "").upper().strip()
    
    
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

@app.get("/state")
async def state():
    return {"status": "active"}

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
            model="gemini-1.5-flash", # Use the stable model ID
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
    description="Extracts structured data from messy titles using AI."
)

app = gr.mount_gradio_app(app, io, path="/")




def main():
    """Entry point for the server as required by the validator."""
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()