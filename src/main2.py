from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
Gemini_API_KEY = os.getenv('Gemini_API_KEY')

from google import genai

client = genai.Client(
    api_key=Gemini_API_KEY,
)
response = client.models.generate_content(
    model='gemini-2.0-flash-exp', contents='How does AI work?'
)
print(response.text)