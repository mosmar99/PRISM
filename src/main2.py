import chainlit as cl
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
Gemini_API_KEY = os.getenv('Gemini_API_KEY')
client = genai.Client(api_key=Gemini_API_KEY)

@cl.on_message
async def main(message):
    """
    This function is triggered whenever a user sends a message in the Chainlit interface.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp', contents=message.content,
        )
        await cl.Message(content=response.text).send()
    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()
