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


# --- ENHANCED GRADIO UI ---

def refine_ui_logic(text):
    """Extraction logic for the manual UI."""
    if not text.strip():
        return "Error: Please enter a product title."
        
    prompt = f"Extract ONLY the brand: {text}. Output one word only."
    try:
        model_id = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text.strip().upper()
    except Exception as e:
        return f"AI Error: {str(e)}"

# Using gr.Blocks to ensure placeholders and styling are preserved
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🛒 Ecommerce Refiner")
    gr.Markdown("Manual testing tool for brand extraction.")
    
    with gr.Column():
        # This explicitly defines the placeholder
        input_box = gr.Textbox(
            label="Product Title", 
            placeholder="Enter messy title here (e.g., NIKE AIR MAX RED 10)...", 
            lines=2
        )
        submit_btn = gr.Button("Extract Brand", variant="primary")
        output_box = gr.Textbox(label="Resulting Brand")
            
    submit_btn.click(fn=refine_ui_logic, inputs=input_box, outputs=output_box)

# Mount the 'demo' block instead of the old 'io' interface
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)