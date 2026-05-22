import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("API key not found. Check your .env file.")
    exit()

URL = "https://openrouter.ai/api/v1/chat/completions"

def test_llm():
    try:
        response = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": "Give ONLY JSON: {\"test\": \"success\"}"
                    }
                ]
            }
        )

        data = response.json()

        print("\nFULL RESPONSE:")
        print(data)

        # Extract model reply
        text = data["choices"][0]["message"]["content"]

        print("\nMODEL OUTPUT:")
        print(text)

    except Exception as e:
        print(" ERROR:", str(e))


if __name__ == "__main__":
    test_llm()