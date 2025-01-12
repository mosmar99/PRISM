import chainlit as cl
import gemini, prompts

async def chat_start():
    welcome_message = (
        "# **General Questions Chat**\n\n"  
        "PrismGPT is a powerful tool designed to assist both healthcare professionals, such as nurses and doctors, and general consumers. "
        "Leveraging the advanced AI capabilities of *Gemini-2.0-Flash* and traditional knowledge graphs like Wikidata. "
        "Note that this chat is tailored for general questions about health and medicine.\n\n"
        "**Get Started:** Simply type your question about medications, treatments, or general health guidelines, and we'll provide you with the information you need. "
        "We're here to help you navigate your healthcare inquiries with confidence.\n\n"
        "**Please note that the information provided here is not a substitute for professional medical advice.**"
    )
    await cl.Message(content=welcome_message).send()

async def extraction(message: cl.Message):
    response = await gemini.send_user_message(prompts.general_chat_prompt(message))
    await cl.Message(content=response).send()