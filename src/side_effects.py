import chainlit as cl
from fuzzywuzzy import process
import asyncio  
import gemini
import sparql

# Load medications from CSV into a list
with open('medications.csv', 'r', encoding='utf-8') as file:
    meds = [line.strip() for line in file if line.strip()] 

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

def create_prompt(input):
    return f"""You are an AI assistant specialized in identifying and extracting medicine names from user text. Given any input, your task is to return only the names of medicines mentioned in the text, correcting minor misspellings or variations if necessary. Follow these rules:

    Identify and extract medicine names (e.g., brand names, generic names, or common trade names of drugs).
    Correct minor misspellings or variations in the names of medicines if they are clearly identifiable (e.g., "asprin" should be "aspirin").
    Do not include descriptions, instructions, or dosages unless explicitly part of the medicine name.
    If no identifiable medicines are mentioned, respond with "No medicines mentioned."
    Do not infer or guess names that are ambiguous or not clearly indicated.
    Translate brandnames into their active chemical/medical substance.
    Return the names as a comma-separated list.
    Examples:

    Input: "I took paracetamol and ibuprofenn this morning for my headache." Output: "paracetamol, ibuprofen"

    Input: "Can I take asprin or tylanol for this?" Output: "aspirin, Tylenol"

    Input: "I used Amoxcillin 500mg for an infection." Output: "Amoxicillin"

    Input: "My doctor prescribed me some medication but I don't remember the name." Output: "No medicines mentioned."

    Input: "Alvedon" Output: "Paracetamol"

    Now, extract the medicines from this input:

    USER_INPUT: {input}"""

async def extraction(message: cl.Message):
    user_inputs.append(message.content)  

    if len(user_inputs) == 1:
        first_input = user_inputs[0]

        # call gemini 2.0 api to extract medications
        llm_filtered_input = await gemini.send_user_message(create_prompt(first_input))

        csv_set = llm_filtered_input.split(',')
        cleaned_set = set({item.strip().lower() for item in csv_set})

        for item in cleaned_set:
            closest_match = process.extractOne(item, meds)[0]
            current_medications.append(closest_match)
        
        first_output = ', '.join(f"'{item}'" for item in current_medications)

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

        # call gemini 2.0 api to extract medications
        llm_filtered_input = await gemini.send_user_message(create_prompt(second_input))

        # Query-Med
        next_medication = process.extractOne(llm_filtered_input, meds)[0]

        await asyncio.sleep(0.4) 
        response_message = (
            f"* **Matched Medication**: `{next_medication}`\n"
        )

        # Output/Display Query-Med
        await cl.Message(content=response_message).send()
    
        next_medication_side_effects = sparql.query_sideeffects_by_name(next_medication)

        next_drug_interactions = str({item: next_medication_side_effects.get(item, "There are NO sideffects") for item in current_medications})

        side_effects_response = await gemini.send_user_message(
            f"### Summary of Side Effects and Drug Interactions with {next_medication}\n\n"
            f"**Below is a summary of the significant drug interaction(s) related to {next_medication}:**\n\n"
            f"- {next_drug_interactions}\n\n"
            "Please ensure the response:\n"
            "- **Does NOT include any introductory phrases like 'Here's a summary...' or similar.**\n"
            "- **Is formatted in a human-readable way**.\n"
            "- **Highlights important points using bullet points or bold text**.\n"
            "- Is written clearly and concisely for easy understanding.\n"
            "- Please, ensure that the following message is included at the end: General Healthcare Warning: Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice."
        )

        await cl.Message(side_effects_response).send()

