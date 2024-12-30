import chainlit as cl
import gemini

async def chat_start():
    welcome_message = (
        "# **Welcome to PrismGPT!**\n\n"  
        "PrismGPT assists nurses and doctors by providing insights into potential "
        "side effects of drug combinations. Powered by cutting-edge AI, it's here "
        "to support your decision-making process.\n\n"
        "This chat is designed to help you with general medical questions."
        "Feel free to ask anything you'd like to know about medications, treatments,"
        "or general health advice.\n\n"
        "Please note that the information provided here is not a substitute for professional medical advice."
    )
    await cl.Message(content=welcome_message).send()

async def extraction(message: cl.Message):
    response = await gemini.send_user_message(message.content)
    await cl.Message(content=response).send()