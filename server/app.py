import os
import random
import uvicorn
import gradio as gr
from fastapi import FastAPI, Request

try:
    from tasks import TASKS
except ImportError:
    from server.tasks import TASKS

app = FastAPI()

VALID_BRANDS = set()
for diff in TASKS:
    for t in TASKS[diff]:
        VALID_BRANDS.add(t["target"]["brand"].upper())




@app.get("/health")
async def health():
    return {"status": "online"}


@app.post("/reset")
async def reset():
    all_tasks = TASKS["easy"] + TASKS["medium"] + TASKS["hard"]
    selected = random.choice(all_tasks)
    return {"observation": selected["input"]}


@app.post("/step")
async def step(request: Request):
    try:
        data = await request.json()
        val = data.get("value", "").upper().strip()

        reward = 1.0 if val in VALID_BRANDS else 0.0

        return {"reward": reward}

    except Exception as e:
        # Never crash
        return {"reward": 0.0, "error": str(e)}


def refine_ui_logic(text):
    if not text.strip():
        return "Error: Please enter a product title."

    text = text.upper()
    for brand in VALID_BRANDS:
        if brand in text:
            return brand

    return "UNKNOWN"


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🛒 Ecommerce Refiner")
    gr.Markdown("Manual testing tool for brand extraction.")

    with gr.Column():
        input_box = gr.Textbox(
            label="Product Title",
            placeholder="Enter messy title here (e.g., NIKE AIR MAX RED 10)...",
            lines=2
        )
        submit_btn = gr.Button("Extract Brand", variant="primary")
        output_box = gr.Textbox(label="Resulting Brand")

    submit_btn.click(fn=refine_ui_logic, inputs=input_box, outputs=output_box)


# Mount UI safely
app = gr.mount_gradio_app(app, demo, path="/")




def main():
    print("🚀 Starting FastAPI server...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()

