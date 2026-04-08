import random
from fastapi import FastAPI, Request
import gradio as gr
import uvicorn

from tasks import TASKS

app = FastAPI()

# Precompute valid brands
VALID_BRANDS = set()
for diff in TASKS:
    for t in TASKS[diff]:
        VALID_BRANDS.add(t["target"]["brand"].upper())


# ---------------- API ENDPOINTS ---------------- #

@app.get("/health")
async def health():
    return {"status": "ok"}


CURRENT_TARGET = ""

@app.post("/reset")
async def reset():
    global CURRENT_TARGET

    all_tasks = TASKS["easy"] + TASKS["medium"] + TASKS["hard"]
    selected = random.choice(all_tasks)

    CURRENT_TARGET = selected["target"]["brand"]

    return {"observation": selected["input"]}


@app.post("/step")
async def step(request: Request):
    try:
        data = await request.json()
        val = data.get("value", "").upper().strip()

        global CURRENT_TARGET

        correct = CURRENT_TARGET.upper()

        
        if val == correct:
            reward = 0.9   # not 1.0
        elif correct in val or val in correct:
            reward = 0.6   # partial match
        elif val != "":
            reward = 0.3   # attempt made
        else:
            reward = 0.1   # empty

        return {"reward": reward}

    except Exception as e:
        return {"reward": 0.1, "error": str(e)}


# ---------------- UI LOGIC ---------------- #

def refine_ui_logic(text):
    if not text.strip():
        return "Error: Please enter a product title."

    text = text.upper()
    for brand in VALID_BRANDS:
        if brand in text:
            return brand

    return "UNKNOWN"


# ---------------- GRADIO UI ---------------- #

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


# Mount UI at root "/"
app = gr.mount_gradio_app(app, demo, path="/")


# ---------------- ENTRY POINT ---------------- #

def main():
    print("🚀 Starting FastAPI server...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()