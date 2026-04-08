import os
import requests
import json
import sys 
import time
from openai import OpenAI

# Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860")
TASK_NAME = "ecommerce-refiner"
BENCHMARK = "scaler-hackathon-v1"

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def run_inference():
    url = SPACE_URL.rstrip('/')
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    # 1. MANDATORY START LOG
    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}", flush=True)

    try:
        # Wait for server
        for i in range(10):
            try:
                if requests.get(f"{url}/health", timeout=5).status_code == 200:
                    break
            except:
                time.sleep(3)
        
        # Step 1: Reset
        res = requests.post(f"{url}/reset", timeout=45).json()
        observation = res.get("observation", "")
        
        # Step 2: Extract Brand
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Extract ONLY the brand name from: {observation}. One word only."}]
        )
        brand = completion.choices[0].message.content.strip().upper()
        
        # Step 3: Step
        step_res = requests.post(f"{url}/step", json={"field": "brand", "value": brand}, timeout=30).json()
        reward = float(step_res.get("reward", 0.0))
        rewards.append(reward)
        steps_taken = 1
        
        # 2. MANDATORY STEP LOG (Must include reward, done, and error)
        print(f"[STEP] step=1 action=brand:{brand} reward={reward:.2f} done=true error=null", flush=True)

        score = reward # Since it's a 1-step task in this check
        success = score >= 1.0

    except Exception as e:
        error_msg = str(e).replace("\n", " ")
        print(f"[STEP] step=1 action=fail reward=0.00 done=true error={error_msg}", flush=True)
    
    finally:
        # 3. MANDATORY END LOG
        rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(f"[END] success={str(success).lower()} steps={steps_taken} score={score:.2f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    run_inference()