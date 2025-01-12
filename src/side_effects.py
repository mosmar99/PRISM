import chainlit as cl
from fuzzywuzzy import process
import asyncio  
import gemini
import sparql
import prompts
from utils import read_meds

async def chat_start():
    welcome_message = (
        "# **Side Effects Identifier Chat**\n\n"  
        "This chat focuses on identifying and specifying significant side effects "
        "between your current medications and any potential additions.\n\n"
        "**Please note that the information provided here is not a substitute for professional medical advice.**\n"
        "## **Get Started:**\n"  
        "List the current medications of your patient in the following format: "
        "`Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`.\n\n"
    )
    await init_globals()
    await cl.Message(content=welcome_message).send()

async def extraction(message: cl.Message):

    global next_medication  
    global next_drug_interactions
    meds = read_meds()

    user_inputs.append(message.content)  

    # Check if the message is asking for further details or if it's an additional query
    if len(user_inputs) > 2:
        additional_query = message.content

        # Ensure context variables are defined or fallback to defaults
        context_summary = (
            f"Current medications: {', '.join(current_medications) or 'None provided yet'}\n"
            f"Next medication: {next_medication or 'None provided yet'}\n"
            f"Next drug interactions: {next_drug_interactions if 'next_drug_interactions' in globals() else 'None provided yet'}"
        )

        # Generate clarification prompt with context
        clarification_prompt = (
            f"### Context Summary:\n{context_summary}\n\n"
            f"Now answer this additional query clearly:\n{additional_query}"
        )

        # Get response from Gemini and display it
        clarification_response = await gemini.send_user_message(clarification_prompt)
        await cl.Message(content=clarification_response).send()
        await show_buttons()
        return


    if len(user_inputs) == 1:
        first_input = user_inputs[0]

        # call gemini 2.0 api to extract medications
        llm_filtered_input = await gemini.send_user_message(prompts.medicine_extraction_prompt(first_input))

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
        llm_filtered_input = await gemini.send_user_message(prompts.medicine_extraction_prompt(second_input))

        # Query-Med
        next_medication = process.extractOne(llm_filtered_input, meds)[0]

        await asyncio.sleep(0.4) 
        response_message = (
            f"* **Matched Medication**: `{next_medication}`\n"
        )

        # Output/Display Query-Med
        await cl.Message(content=response_message).send()
    
        next_medication_side_effects = sparql.query_sideeffects_by_name(next_medication)
        next_drug_interactions = str({item: next_medication_side_effects.get(item, "No *significant* sideeffects") for item in current_medications})

        side_effects_response = await gemini.send_user_message(prompts.current_next_interactions_prompt(next_drug_interactions, next_medication))

        await cl.Message(side_effects_response).send()

        await show_buttons()

async def show_buttons():
    actions = [
        cl.Action(
            name="query_again_se",
            value="restart",
            description="Start a new query with the initial question.",
            label="Query Again"
        ),
        cl.Action(
            name="ask_details_se",
            value="details",
            description="Ask for further clarification.",
            label="Ask for Further Details"
        ),
    ]

    await cl.Message(
        content="## **What would you like to do next?**",
        actions=actions
    ).send()

async def init_globals():
    global user_inputs, current_medications, next_medication, next_drug_interactions
    user_inputs = []
    current_medications = []
    next_medication = None
    next_drug_interactions = None

@cl.action_callback("query_again_se")
async def handle_query_again(action):
    query_again_message = (
        "## **Query Again:**\n"  
        "Please, list the current medications of your patient in the following format: "
        "`Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`"
    )
    await init_globals()
    await cl.Message(
        content=query_again_message,
    ).send()

@cl.action_callback("ask_details_se")
async def handle_ask_details(action):
    await cl.Message(
        content="Please specify the details you would like to know more about."
    ).send()
