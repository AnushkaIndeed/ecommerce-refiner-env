import os
import requests
import json
import sys 
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

SPACE_URL = "https://huggingface.co/spaces/AnushkaK11/ecommerce-refiner-env" 

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


def run_inference():
    print(f"[START] task={MODEL_NAME}", flush=True)
    
    try:
        reset_resp = requests.post(f"{SPACE_URL}/reset", timeout=30)
        
        reset_resp.raise_for_status() 
        
        observation = reset_resp.json().get("observation")
        print(f"[STEP] step=1 reward=0.0 observation='{observation}'", flush=True)

        # AI LOGIC
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Extract Brand: '{observation}'"}]
        )
        brand_value = response.choices[0].message.content.strip().upper()

        # STEP SUBMISSION
        payload = {"field": "brand", "value": brand_value}
        step_resp = requests.post(f"{SPACE_URL}/step", json=payload, timeout=30)
        step_resp.raise_for_status()

        result = step_resp.json()
        reward = result.get("reward", 0.0)
        
        print(f"[STEP] step=2 reward={reward} action='brand:{brand_value}'", flush=True)
        print(f"[END] task={MODEL_NAME} score={reward} steps=2", flush=True)

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}", file=sys.stderr)
        print(f"[END] task={MODEL_NAME} score=0.0 steps=0", flush=True)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        print(f"[END] task={MODEL_NAME} score=0.0 steps=0", flush=True)

if __name__ == "__main__":
    run_inference()