# app/services/google_service.py
import os
import requests
from app.exceptions.errors import GoogleAPIError
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash-latest"

def get_ai_response(message: str) -> str:
    if not GOOGLE_API_KEY:
        raise GoogleAPIError("Google API Key not configured")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": message}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except requests.exceptions.RequestException as e:
        raise GoogleAPIError(f"Error communicating with Google AI Studio: {e}")
