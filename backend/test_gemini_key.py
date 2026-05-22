import os
from google import genai

# 1. SETUP - Replace with your key
API_KEY = "AIzaSyC7GKnN0IxmFZAwQ_XcGO28sQSCmwky9O0" 

client = genai.Client(api_key=API_KEY)

def test_api_connection():
    print("--- Starting Gemini API Test ---")
    
    # STEP 1: Test Model Access
    try:
        print("[1/2] Checking model access...")
        print(os.getenv("OPENROUTER_API_KEY"))
        models = client.models.list()
        print("SUCCESS: API Key is valid and can access models.")
        
    except Exception as e:
        # Using ascii() to prevent further encoding crashes
        print(f"ERROR at Authentication: {ascii(str(e))}")
        return

    # STEP 2: Test Content Generation
    try:
        print("[2/2] Testing content generation (quota check)...")
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Say 'API is working' in one sentence."
        )
        print("SUCCESS: Generation working!")
        print(f"Model Response: {response.text.strip()}")
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            print("FAILED: Key is valid, but your QUOTA is exhausted (Error 429).")
            print("Tip: Wait 60 seconds or create a NEW project in AI Studio.")
        else:
            print(f"FAILED at Generation: {ascii(error_msg)}")

if __name__ == "__main__":
    test_api_connection()