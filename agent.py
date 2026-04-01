import requests
from google import genai

client = genai.Client(
    api_key="GOOGLE_API_KEY",
    http_options={'api_version': 'v1'} 
)


MODEL_ID = "gemini-2.5-flash"

BASE_URL = "https://anushkak11-ecommerce-refiner.hf.space"

def run_agent():
    try:
        # --- PHASE 1: GET THE TASK ---
        print("📦 Fetching task...")
        reset_resp = requests.post(f"{BASE_URL}/reset")
        messy_string = reset_resp.json().get("observation")
        print(f"Target: {messy_string}")

        # --- PHASE 2: AI REASONING ---
        prompt = f"Extract the Brand from: '{messy_string}'. Return ONLY the brand name."
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        
        brand_value = response.text.strip().upper()
        print(f"🤖 AI identified Brand: {brand_value}")

        # --- PHASE 3: SUBMIT ---
        payload = {"field": "brand", "value": brand_value}
        refine_resp = requests.post(f"{BASE_URL}/refine", json=payload)
        
        if refine_resp.status_code == 200:
            print(f"✅ Success! Reward: {refine_resp.json().get('reward')}")
        else:
            print(f"❌ Submission Error: {refine_resp.text}")

    except Exception as e:
        print(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    run_agent()