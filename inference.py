import os
import requests
import json
import sys 
import time
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL","http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
HF_TOKEN = os.getenv("HF_TOKEN")

SPACE_URL = "https://huggingface.co/spaces/AnushkaK11/ecommerce-refiner-env" 

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def run_inference():
    print(f"[START] task={MODEL_NAME}", flush=True)
    
    try:
        # Step 1: Reset 
        response = requests.post(f"{SPACE_URL}/reset", timeout=45)
        response.raise_for_status()
        data = response.json()
        observation = data.get("observation", "")

        print(f"[STEP] step=1 reward=0.0 observation='{observation}'", flush=True)

        # Step 2: AI Thinking
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Extract the Brand name from this product title: {observation}"}]
        )
        brand = completion.choices[0].message.content.strip().upper()

        # Step 3: Submission 
        payload = {"field": "brand", "value": brand}
        step_response = requests.post(f"{SPACE_URL}/step", json=payload, timeout=30)
        step_response.raise_for_status()
        
        result = step_response.json()
        reward = result.get("reward", 0.0)

        print(f"[STEP] step=2 reward={reward} action='brand:{brand}'", flush=True)
        print(f"[END] task={MODEL_NAME} score={reward} steps=2", flush=True)

    except requests.exceptions.RequestException as e:
        
        print(f"Network Error: {e}", file=sys.stderr)
        print(f"[END] task={MODEL_NAME} score=0.0 steps=0", flush=True)
        sys.exit(0) 
    except Exception as e:
        
        print(f"Unexpected Error: {str(e)}", file=sys.stderr)
        print(f"[END] task={MODEL_NAME} score=0.0 steps=0", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    run_inference()