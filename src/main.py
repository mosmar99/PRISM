import chainlit as cl
from chainlit.types import ThreadDict
import gemini
import side_effects as side_effect_chat
import general_chat as general_chat
from sparql import get_all_meds
import alternative_medication

chat = None

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="General Questions",
            markdown_description="Ask General Medical Questions.",
            icon="public/general_questions_icon.svg",
        ),
        cl.ChatProfile(
            name="Side Effects Identifier",
            markdown_description="Identify Significant Side Effects Between Interacting Medicines.",
            icon="public/side_effects_icon.svg",
        ),
        cl.ChatProfile(
            name="Alternative Medications",
            markdown_description="Suggest Alternative Medications Without Side Effects.",
            icon="public/alternative_medications_icon.svg",
        ),
        cl.ChatProfile(
            name="Medication Recommendation",
            markdown_description="Suggest Medications Given User Defined Symptoms.",
            icon="public/recomendation_icon.svg",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    global chat
    chat_profile = cl.user_session.get("chat_profile")

    if chat_profile == "General Questions":
        chat = general_chat 
        await chat.chat_start()

    if chat_profile == "Side Effects Identifier":
        chat = side_effect_chat
        await chat.chat_start()

    if chat_profile == "Alternative Medications":
        chat = alternative_medication
        await chat.chat_start()

@cl.on_message
async def on_message(message: cl.Message):
    await chat.extraction(message)

# try catch get all meds
try:
    get_all_meds()
except:
    with open('medications.csv', 'r', encoding='utf-8') as file:
        meds = [line.strip() for line in file if line.strip()] 