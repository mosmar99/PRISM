import chainlit as cl
from fuzzywuzzy import process
import asyncio  # Import asyncio for sleep functionality

# Load medications from CSV into a list
with open('medications.csv', 'r', encoding='utf-8') as file:
    meds = [line.strip() for line in file if line.strip()]  # Read each line and strip whitespace

@cl.on_chat_start
async def chat_start():
    welcome_message = (
        "# **Welcome to PrismGPT!**\n\n"  
        "PrismGPT assists nurses and doctors by providing insights into potential "
        "side effects of drug combinations. Powered by cutting-edge AI, it's here "
        "to support your decision-making process.\n\n"
        "## **Get Started:**\n"  
        "Please, list the current medications of your patient in the following format: "
        "`Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`"
    )
    await cl.Message(content=welcome_message).send()

user_inputs = []
current_medications = []
next_medication = None

@cl.on_message
async def extraction(message: cl.Message):
    user_inputs.append(message.content)  

    if len(user_inputs) == 1:
        first_input = user_inputs[0]
        csv_set = set(first_input.split(','))
        cleaned_set = {item.strip() for item in csv_set}

        for item in cleaned_set:
            closest_match = process.extractOne(item, meds)[0]
            current_medications.append(closest_match)
        
        first_output = ', '.join(f"'{item}'" for item in current_medications)
        await asyncio.sleep(0.25) 

        # Extracted medications
        response_message_1 = (
            f"* **Matched Medications**: `{first_output}`"
        )
        await cl.Message(content=response_message_1).send()
        await asyncio.sleep(0.5) 

        # Q2
        response_message_2 = (
            "**Please, enter the name of the medication you would like to check for interactions**:"
        )
        await cl.Message(content=response_message_2).send()

    if len(user_inputs) == 2:
        second_input = user_inputs[1]

        # Find the closest match to the user's input
        next_medication = process.extractOne(second_input, meds)[0]

        await asyncio.sleep(0.4) 
        response_message = (
            f"* **Matched Medication**: `{next_medication}`\n"
        )
    
        await cl.Message(content=response_message).send()
