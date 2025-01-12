import prompts
import gemini
import sparql
import chainlit as cl
import time
from utils import read_meds
from fuzzywuzzy import process
import ast

user_inputs = 0
first_input = ""
second_input = ""
final = False
meds = read_meds()


async def chat_start():
    global user_inputs, final, first_input, second_input

    final = False
    user_inputs = 0
    first_input = ""
    second_input = ""

    welcome_message = (
        "# **Alternative Medication Chat**\n\n"  
        "This chat identifies potential negative side effects of your current medications. "
        "If any significant interactions or side effects are detected, we will provide you with equivalent alternative medications to consider. \n\n"
        "**Please note that the information provided here is not a substitute for professional medical advice.**\n"
        "## **Get Started:**\n"  
        "List the current medications of your patient in the following format: "
        "`Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`.\n\n"
    )

    await cl.Message(content=welcome_message).send()

async def get_information():

    global user_inputs, final, first_input, second_input
    message = ""

    results = []
    msg = await cl.Message(content="Looking for safe alternatives!").send()

    list1 = [item.strip() for item in first_input.split(',')]
    list2 = [item.strip() for item in second_input.split(',')]

    list1 = [ast.literal_eval(item) for item in list1]
    list2 = [ast.literal_eval(item) for item in list2]

    if(list1[0].strip() == "No medicines mentioned." or second_input.strip() == "No medicines mentioned."):
        await cl.Message(content="Seems like something have gone wrong, chat will restart sorry for the inconvenience").send()
        time.sleep(.75)
        await chat_start()
        return
    
    for medicine in list1:
        results.append(sparql.get_alternatives(medicine, list2[0]))

    intersection = set(results[0]) 
    for lst in results[1:]:
        intersection.intersection_update(lst) 

    intersection = list(intersection)

    intersectionString = f"SAFE ALTERNATIVES FOR: {list2[0]} WITH REGARDS TO: {', '.join(list1)} \n\n INPUT: " + str(intersection)

    prompt = prompts.alt_med_summary_prompt(intersectionString)

    message = await get_output(prompt)

    msg.content = message
    await msg.update()
    final = "More"
    await show_buttons()

    return
    
async def get_output(input):
    try:
        return await gemini.send_user_message(input)
    except:
        await cl.Message(content="Seems like something have gone wrong, chat will restart sorry for the inconvenience").send()
        time.sleep(.75)
        await chat_start()

async def parse_user_input(input):
    global user_inputs, first_input, second_input, meds
    prompt = prompts.medicine_extraction_prompt(input)

    # Get response from Gemini and display it
    extracted_input = await get_output(prompt)

    if "No medicines mentioned" in extracted_input:
        response = "No medications mentioned. Please list the current medications of your patient."
        await cl.Message(content=response).send()
        await show_buttons()
        return

    csv_set = extracted_input.split(',')
    cleaned_set = set({item.strip().lower() for item in csv_set})

    temp = []

    for item in cleaned_set:
        closest_match = process.extractOne(item, meds)[0]
        temp.append(closest_match)
    
    extracted_input = ', '.join(f"'{item}'" for item in temp)

    clarifiying_output = (
        f"* **Patients current / proposed medications**: `{extracted_input}`\n\n"
    )

    await cl.Message(content=clarifiying_output).send()

    if first_input == "":
        first_input = extracted_input
        time.sleep(1)
        await cl.Message(content="**Please, enter the name of the proposed medication you would like to check**: `Medicine_A`").send()
    else:
        second_input = extracted_input

    if (second_input != ""):
        await get_information()

async def extraction(message: cl.Message):
    global user_inputs, first_input, second_input

    input = message.content


    if final == "More":

        prompt = (
            "User has now finished extracting the wanted information and wishes to have a general chat about the results"
            "Make sure that the conversation is related to medications, alert user otherwise."
            f"Heres the user defined input:{input}"
            "please answer concisely and include the following warning ALWAYS:"
            "\n\n*General Healthcare Warning:* Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice"
        )
        response = await get_output(prompt)
        await cl.Message(content=response).send()
        await show_buttons()
        return

    await parse_user_input(input)

async def show_buttons():
    actions = [
        cl.Action(
            name="query_again_am",
            value="restart",
            description="Start a new query with the initial question.",
            label="Query Again"
        ),
        cl.Action(
            name="ask_details_am",
            value="details",
            description="Ask for further clarification.",
            label="Ask for Further Details"
        ),
    ]

    await cl.Message(
        content="## **What would you like to do next?**",
        actions=actions
    ).send()

@cl.action_callback("query_again_am")
async def handle_query_again(action):
    await chat_start()

@cl.action_callback("ask_details_am")
async def handle_ask_details(action):
    global final
    final = "More"
    await cl.Message(
        content="Please specify the details you would like to know more about."
    ).send()