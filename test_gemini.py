from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say Hello in JSON",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0
    )
)

print(response.text)