import os
import requests
import time

# Validator connects to your app container here
SPACE_URL = os.getenv("SPACE_URL", "http://127.0.0.1:7860")


def extract_brand(observation: str) -> str:
    """
    Robust brand extraction:
    - Handles multiple brands
    - Returns last occurring brand (better accuracy)
    - Safe fallback to UNKNOWN
    """
    try:
        if not observation:
            return "UNKNOWN"

        text = observation.upper()
        brands = ["NIKE", "ADIDAS", "PUMA", "ZARA", "APPLE"]

        found = []
        for brand in brands:
            if brand in text:
                found.append((text.rfind(brand), brand))

        if found:
            return sorted(found)[-1][1]

        return "UNKNOWN"

    except Exception:
        return "UNKNOWN"


def run_inference():
    url = SPACE_URL.rstrip('/')
    print("[START] task=ecommerce-refiner env=scaler-hackathon-v1", flush=True)

    rewards = []
    success = False
    score = 0.0
    steps_taken = 0

    try:
        # ✅ 1. Wait for server to be live
        server_live = False
        for _ in range(20):
            try:
                res = requests.get(f"{url}/health", timeout=2)
                if res.status_code == 200:
                    server_live = True
                    break
            except Exception:
                time.sleep(3)

        if not server_live:
            raise Exception("Server failed to start within timeout")

        # ✅ 2. Reset task
        res = requests.post(f"{url}/reset", timeout=10).json()
        observation = res.get("observation", "")

        # ✅ 3. Extract brand safely
        brand = extract_brand(observation)

        # ✅ 4. Submit prediction
        step_res = requests.post(
            f"{url}/step",
            json={"field": "brand", "value": brand},
            timeout=10
        ).json()

        reward = float(step_res.get("reward", 0.0))

        rewards.append(reward)
        steps_taken = 1
        score = reward
        success = (reward >= 1.0)

        print(
            f"[STEP] step=1 action=brand:{brand} reward={reward:.2f} done=true error=null",
            flush=True
        )

    except Exception as e:
        print(
            f"[STEP] step=1 action=error reward=0.00 done=true error={str(e)}",
            flush=True
        )

    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(
            f"[END] success={str(success).lower()} steps={steps_taken} score={score:.2f} rewards={rewards_str}",
            flush=True
        )


if __name__ == "__main__":
    run_inference()