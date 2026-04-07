import os
import requests
import json
import sys # Added for flushing
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

SPACE_URL = "https://huggingface.co/spaces/AnushkaK11/ecommerce-refiner-env" 

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def run_inference():
   
    task_id = MODEL_NAME if MODEL_NAME else "ecommerce_refinement"
    
    print(f"[START] task={task_id}", flush=True)
    
    try:
        # Reset the environment
        reset_resp = requests.post(f"{SPACE_URL}/reset")
        if reset_resp.status_code != 200:
            print(f"[END] task={task_id} score=0.0 steps=0", flush=True)
            return
            
        observation = reset_resp.json().get("observation", "")
        
        # 2. REQUIRED STEP BLOCK (Observation)
        print(f"[STEP] step=1 reward=0.0 observation='{observation}'", flush=True)

        # AI Logic
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user", 
                "content": f"Extract the Brand from: '{observation}'. Return ONLY the brand name in uppercase."
            }]
        )
        brand_value = response.choices[0].message.content.strip().upper()

        # Submit Step
        payload = {"field": "brand", "value": brand_value}
        step_resp = requests.post(f"{SPACE_URL}/step", json=payload)
        
        result = step_resp.json()
        reward = result.get("reward", 0.0)

        # 3. REQUIRED STEP BLOCK (Action)
        print(f"[STEP] step=2 reward={reward} action='brand:{brand_value}'", flush=True)

        # 4. REQUIRED END BLOCK
        print(f"[END] task={task_id} score={reward} steps=2", flush=True)

    except Exception as e:
        # 5. REQUIRED END BLOCK ON FAILURE
        print(f"[END] task={task_id} score=0.0 steps=0", flush=True)
        print(f"Error: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    run_inference()