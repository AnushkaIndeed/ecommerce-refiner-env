import random
from fastapi import FastAPI, Request
import gradio as gr
import uvicorn


try:
    from tasks import TASKS as RAW_TASKS
except:
    from server.tasks import TASKS as RAW_TASKS

TASKS = []
for diff in RAW_TASKS:
    for t in RAW_TASKS[diff]:
        TASKS.append({
            "input": t["input"],
            "target": t["target"]["brand"].upper()
        })

app = FastAPI()

CURRENT_TASK = None


# ---------------- API ENDPOINTS ---------------- #

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset")
async def reset():
    global CURRENT_TASK

    CURRENT_TASK = random.choice(TASKS)

    return {"observation": CURRENT_TASK["input"]}


@app.post("/step")
async def step(request: Request):
    try:
        global CURRENT_TASK

        data = await request.json()
        val = data.get("value", "").upper().strip()
        correct = CURRENT_TASK["target"]

        if val == correct:
            reward = 0.9
        elif correct in val or val in correct:
            reward = 0.6
        elif val != "":
            reward = 0.3
        else:
            reward = 0.1

        return {"reward": reward}

    except Exception as e:
        return {"reward": 0.1, "error": str(e)}


# ---------------- UI LOGIC ---------------- #

def refine_ui_logic(text):
    if not text.strip():
        return "Error: Please enter a product title."

    text = text.upper()

    for task in TASKS:
        if task["target"] in text:
            return task["target"]

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


# Mount UI
app = gr.mount_gradio_app(app, demo, path="/")


# ---------------- ENTRY POINT ---------------- #

def main():
    print("🚀 Starting FastAPI server...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()