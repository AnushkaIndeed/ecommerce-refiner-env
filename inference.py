import os
import requests
import sys 
import time
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
HF_TOKEN = os.getenv("HF_TOKEN")
# Validator uses localhost/127.0.0.1 to bridge the two containers
SPACE_URL = os.getenv("SPACE_URL", "http://127.0.0.1:7860")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def run_inference():
    url = SPACE_URL.rstrip('/')
    print(f"[START] task=ecommerce-refiner env=scaler-hackathon-v1 model={MODEL_NAME}", flush=True)
    
    rewards = []
    success = False
    score = 0.0
    steps_taken = 0

    try:
        # 1. Wait for Server (Patient Loop)
        server_live = False
        for i in range(20):
            try:
                if requests.get(f"{url}/health", timeout=2).status_code == 200:
                    server_live = True
                    break
            except:
                time.sleep(3)
        
        if not server_live:
            raise Exception("Server failed to start within 60 seconds")

        # 2. Reset Task
        res = requests.post(f"{url}/reset", timeout=10).json()
        observation = res.get("observation", "")

        # 3. AI Extraction Logic
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Extract ONLY the brand name: {observation}. One word only."}]
        )
        brand = completion.choices[0].message.content.strip().upper()

        # 4. Submission
        step_res = requests.post(f"{url}/step", json={"field": "brand", "value": brand}, timeout=10).json()
        reward = float(step_res.get("reward", 0.0))
        
        rewards.append(reward)
        steps_taken = 1
        score = reward
        success = (reward >= 1.0)

        print(f"[STEP] step=1 action=brand:{brand} reward={reward:.2f} done=true error=null", flush=True)

    except Exception as e:
        print(f"[STEP] step=1 action=error reward=0.00 done=true error={str(e)}", flush=True)
    
    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(f"[END] success={str(success).lower()} steps={steps_taken} score={score:.2f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    run_inference()