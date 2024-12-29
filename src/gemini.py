import google.generativeai as genai
import json
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv('API_KEY'))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

async def send_user_message(message):
  try:
    response = chat_session.send_message(message)
    return response._result.candidates[0].content.parts[0].text
  except:
    return "400"
