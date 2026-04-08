import os
import requests
import time
from openai import OpenAI

API_KEY = os.environ.get("API_KEY")
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")


SPACE_URL = "http://127.0.0.1:7860"


client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)


def extract_brand(observation: str) -> str:
    try:
        if not observation:
            return "UNKNOWN"

        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": f"Extract ONLY the brand name from this product title: {observation}. Return one word only."
            }]
        )

        brand = response.choices[0].message.content.strip().upper()

        if brand:
            return brand

    except Exception:
        pass  # fallback below

    # Fallback
    try:
        text = observation.upper()
        brands = ["NIKE", "ADIDAS", "PUMA", "ZARA", "APPLE"]

        found = []
        for b in brands:
            if b in text:
                found.append((text.rfind(b), b))

        if found:
            return sorted(found)[-1][1]

    except:
        pass

    return "UNKNOWN"


def run_inference():
    url = SPACE_URL.rstrip('/')
    print("[START] task=ecommerce-refiner env=scaler-hackathon-v1", flush=True)

    rewards = []
    success = False
    score = 0.0
    steps_taken = 0

    try:
        # Wait for server
        server_live = False
        for _ in range(20):
            try:
                res = requests.get(f"{url}/health", timeout=2)
                if res.status_code == 200:
                    server_live = True
                    break
            except:
                time.sleep(3)

        if not server_live:
            raise Exception("Server failed to start")

        # Reset
        res = requests.post(f"{url}/reset", timeout=10)
        res.raise_for_status()
        data = res.json()
        observation = data.get("observation", "")

        # Extract using LLM
        brand = extract_brand(observation)

        # Step
        step_res = requests.post(
            f"{url}/step",
            json={"field": "brand", "value": brand},
            timeout=10
        )
        step_res.raise_for_status()
        data = step_res.json()
        reward = float(data.get("reward", 0.0))

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