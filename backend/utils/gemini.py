

# # ✅ FIX 1: FULL UPDATED `gemini.py` (VERY IMPORTANT)

# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# import json

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-2.5-flash")


# def clean_json(text):
#     """
#     Remove markdown / unwanted text from Gemini output
#     """
#     text = text.strip()

#     # remove ```json or ```
#     text = text.replace("```json", "").replace("```", "")

#     return text


# def generate_diet_plan(user, consumed_calories):
#     prompt = f"""
#     You are a professional nutritionist.

#     Return ONLY JSON (no explanation).

#     {{
#       "daily_calories": number,
#       "remaining_calories": number,
#       "meals": {{
#         "breakfast": "...",
#         "lunch": "...",
#         "dinner": "..."
#       }},
#       "tips": ["...", "..."]
#     }}

#     User:
#     Age: {user.get('age')}
#     Weight: {user.get('weight')}
#     Height: {user.get('height')}
#     Goal: {user.get('goal')}
#     Activity: {user.get('activity')}

#     Consumed: {consumed_calories}
#     """

#     try:
#         response = model.generate_content(prompt)

#         text = clean_json(response.text)

#         try:
#             return json.loads(text)
#         except:
#             return {
#                 "daily_calories": 2000,
#                 "remaining_calories": 2000 - consumed_calories,
#                 "meals": {
#                     "breakfast": "Healthy oats + fruits",
#                     "lunch": "Rice + dal + vegetables",
#                     "dinner": "Light salad + roti"
#                 },
#                 "tips": ["Drink water", "Avoid junk food"],
#                 "error": "JSON parse failed"
#             }

#     except Exception as e:
#         return {
#             "daily_calories": 2000,
#             "remaining_calories": 2000 - consumed_calories,
#             "meals": {
#                 "breakfast": "Fallback meal",
#                 "lunch": "Fallback meal",
#                 "dinner": "Fallback meal"
#             },
#             "tips": ["Error occurred"],
#             "error": str(e)
#         }



import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"


def clean_json(text):
    """
    Remove markdown / unwanted text from LLM output
    """
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")
    return text


def generate_diet_plan(user, consumed_calories):
    prompt = f"""
    You are a professional nutritionist.

    Return ONLY JSON (no explanation).

    {{
      "daily_calories": number,
      "remaining_calories": number,
      "meals": {{
        "breakfast": "...",
        "lunch": "...",
        "dinner": "..."
      }},
      "tips": ["...", "..."]
    }}

    User:
    Age: {user.get('age')}
    Weight: {user.get('weight')}
    Height: {user.get('height')}
    Goal: {user.get('goal')}
    Activity: {user.get('activity')}

    Consumed: {consumed_calories}
    """

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
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        )

        data = response.json()

        # Handle API errors safely
        if "error" in data:
            return {
                "daily_calories": 2000,
                "remaining_calories": 2000 - consumed_calories,
                "meals": {
                    "breakfast": "Fallback meal",
                    "lunch": "Fallback meal",
                    "dinner": "Fallback meal"
                },
                "tips": ["Error occurred"],
                "error": data["error"]["message"]
            }

        text = data["choices"][0]["message"]["content"]
        text = clean_json(text)

        try:
            return json.loads(text)
        except:
            return {
                "daily_calories": 2000,
                "remaining_calories": 2000 - consumed_calories,
                "meals": {
                    "breakfast": "Healthy oats + fruits",
                    "lunch": "Rice + dal + vegetables",
                    "dinner": "Light salad + roti"
                },
                "tips": ["Drink water", "Avoid junk food"],
                "error": "JSON parse failed"
            }

    except Exception as e:
        return {
            "daily_calories": 2000,
            "remaining_calories": 2000 - consumed_calories,
            "meals": {
                "breakfast": "Fallback meal",
                "lunch": "Fallback meal",
                "dinner": "Fallback meal"
            },
            "tips": ["Error occurred"],
            "error": str(e)
        }