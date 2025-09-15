
import base64
import requests
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# API Key and URL
api_key = os.getenv("GEMINI_API_KEY")
api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent'

# Function to analyze image
def analyze_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return f"Error opening image: {e}"

    request_body = {
        "contents": [{
            "parts": [
                {"text": "Describe this image in detail. What might be its origin or context? Analyze its contents thoroughly."},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",  # Update if using PNG, etc.
                        "data": base64_image
                    }
                }
            ]
        }]
    }

    try:
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=request_body,
            params={'key': api_key}
        )
    except Exception as e:
        return f"Error sending request: {e}"

    if response.status_code == 200:
        data = response.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
        return "No description found in response."
    else:
        return f"Error: {response.status_code} - {response.text}"


# Input image path interactively
#image_path = r"C:\Users\kazi_\Downloads\news.jpeg"
#description = analyze_image(image_path)
#print("Image Analysis Result:", description)

