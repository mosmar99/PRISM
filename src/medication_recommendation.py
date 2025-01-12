import chainlit as cl
from fuzzywuzzy import process
import gemini
import prompts
import sparql

from utils import read_symptoms

current_symptoms = []

async def chat_start():
    welcome_message = (
        "# **Medication Recommendation Chat**\n\n"  
        "This chat provides common and legal medications used to treat user specified symptoms.\n\n"
        "**Please note that the information provided here is not a substitute for professional medical advice.**\n"
        "## **Get Started:**\n"  
        "List the current medications of your patient in the following format: "
        "`Symptom_A, Symptom_B, Symptom_C, ..., Symptom_Z`.\n\n"
    )
    await init_globals()
    await cl.Message(content=welcome_message).send()

async def extraction(message: cl.Message):
    symptoms = read_symptoms()

    # call gemini 2.0 api to extract symptoms
    llm_filtered_input = await gemini.send_user_message(prompts.symptoms_extraction_prompt(message.content))
    if "No symptoms mentioned" in llm_filtered_input:
        response = "No symptoms mentioned. Please list the current symptoms of your patient."
        await cl.Message(content=response).send()
        await show_buttons()
        return

    csv_set_english = llm_filtered_input.split(',')
    llm_latin_translation = await gemini.send_user_message(prompts.symptoms_convert_to_latin(csv_set_english))
    csv_set_latin = llm_latin_translation.split(',')

    cleaned_set_combined = {(latin, english) for latin, english in zip(csv_set_latin, csv_set_english)}
 
    for item in cleaned_set_combined:
        first_element = item[0]
        second_element = item[1]

        match_first = process.extractOne(first_element, symptoms)
        match_second = process.extractOne(second_element, symptoms)

        if match_first[1] > match_second[1]:
            closest_match = match_first[0]
        else:
            closest_match = match_second[0]

        current_symptoms.append(closest_match)

    first_output = ', '.join(f"'{item}'" for item in current_symptoms)

    # Extracted medications
    response_message_1 = (
        f"* **Matched Symptoms**: `{first_output}`"
    )
    await cl.Message(content=response_message_1).send()

    symptom_to_medications = {}

    for symptom in current_symptoms:
        symptom_code = sparql.query_symptom_id(symptom)
        medication_list = sparql.find_medicine_on_symptom_treated(symptom_code)
        symptom_to_medications[symptom] = medication_list


    response = await gemini.send_user_message(prompts.symptoms_med_recommendation_prompt(symptom_to_medications))
    await cl.Message(content=response).send()

    await show_buttons()

async def show_buttons():
    actions = [
        cl.Action(
            name="query_again_mr",
            value="restart",
            description="Start a new query with the initial question.",
            label="Query Again",
            payload={},
        ),
    ]

    await cl.Message(
        content="## **What would you like to do next?**",
        actions=actions
    ).send()

async def init_globals():
    global current_symptoms
    current_symptoms = []

@cl.action_callback("query_again_mr")
async def handle_query_again(action):
    query_again_message = (
        "## **Query Again:**\n"
        "Please, list your current symptoms in the following format: `Symptom_A, Symptom_B, Symptom_C, ..., Symptom_Z`"
    )
    await init_globals()
    await cl.Message(
        content=query_again_message,
    ).send()





