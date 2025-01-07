import prompts
import gemini
import sparql
import chainlit as cl
import time

user_inputs = 0
first_input = ""
second_input = ""
final = False


async def chat_start():
    global user_inputs, final, first_input, second_input

    final = False
    user_inputs = 0
    first_input = ""
    second_input = ""

    welcome_message = (
        "# **Welcome to PrismGPT!**\n\n"  
        "PrismGPT is here to assist nurses and doctors by providing insights into potential "
        "side effects of drug combinations and suggesting safe alternatives where necessary. "
        "Powered by cutting-edge AI: *Gemini-2.0-Flash*.\n\n"
        "## **Get Started:**\n"  
        "List the current medications of your patient in the following format: "
        "`Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`.\n\n"
        "Feel free to enter multiple medications, and PrismGPT will analyze the combinations to identify any potential risks and propose safer alternatives if needed."
    )
    await cl.Message(content=welcome_message).send()

async def user_satisfaction(input):

    global user_inputs, final, first_input, second_input

    prompt = prompts.user_satisfaction_prompt(input)

    satisfied = await get_output(prompt)
    satisfied = satisfied.strip()

    message = ""

    if satisfied.strip() == "No":
        user_inputs = 0

        prompt = (
            f"User was disatisfied with our results please, give them a nice short consise message telling them sorry and that we shall try again, mention that they should re enter input, maybe and some nice emoji"
        )
        message = await get_output(prompt)
        
        if second_input == "":
            first_input = ""
        else:
            second_input = ""
        await cl.Message(content=message).send()
        return

    if not final:
        prompt = (
            f"User was happy with our results, please create a nice message like 2-3 sentances and include this part at the end:"
            f"Now list the new proposed medication of your patient in the same format: `Medicine_A`.\n\n"
        )
        message = await get_output(prompt)
        user_inputs = user_inputs + 1
        final = True
        await cl.Message(content=message).send()
        return
    
    else:
        results = ""
        msg = await cl.Message(content="Thinking...").send()

        list = [item.strip() for item in first_input.split(',')]
        list2 = [item.strip() for item in second_input.split(',')]

        second_input = list2[0]

        print(list[0])
        if(list[0].strip() == "No medicines mentioned." or second_input.strip() == "No medicines mentioned."):
            await cl.Message(content="Seems like something have gone wrong, chat will restart sorry for the inconvenience").send()
            time.sleep(.75)
            await chat_start()
            return
        
        for medicine in list:
            results = results + "\n\n INPUT:" + sparql.get_alternatives(medicine, second_input)

        prompt = prompts.alt_med_summary_prompt(results)

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
    global user_inputs, first_input, second_input
    prompt = prompts.medicine_extraction_prompt(input)

    # Get response from Gemini and display it
    extracted_input = await get_output(prompt)
    clarifiying_output = (
        f"* **Patients current / proposed medications**: `{extracted_input}`\n\n"
        f"Does that look right? Please answer `yes or no`, keep in mind active substances does not equal brand names."
    )

    if first_input == "":
        first_input = extracted_input
    else:
        second_input = extracted_input

    user_inputs = user_inputs + 1
    await cl.Message(content=clarifiying_output).send()

async def extraction(message: cl.Message):
    global user_inputs

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

    if user_inputs % 2 == 0:
        await parse_user_input(input)
        return

    if user_inputs % 2 == 1:
        await user_satisfaction(input)
        return

async def show_buttons():
    actions = [
        cl.Action(
            name="query_again_am",
            value="restart",
            description="Start a new query with the initial question.",
            label="Query Again"
        ),
        cl.Action(
            name="ask_details",
            value="details",
            description="Ask for further clarification.",
            label="Ask for Further Details"
        ),
    ]

    await cl.Message(
        content="## **What would you like to do next?**",
        actions=actions
    ).send()

@cl.action_callback("query_again")
async def handle_query_again(action):
    await chat_start()


@cl.action_callback("ask_details")
async def handle_ask_details(action):
    global final
    final = "More"
    await cl.Message(
        content="Please specify the details you would like to know more about."
    ).send()

