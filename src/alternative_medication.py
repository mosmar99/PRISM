import prompts
import gemini
import sparql
import chainlit as cl

user_inputs = 0
first_input = ""
second_input = ""
final = False

# patients current medication -> proposed new medication

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

    satisfied = await gemini.send_user_message(prompt)
    satisfied = satisfied.strip()
    print(satisfied.strip() == "No")

    message = ""

    if satisfied == "No":
        user_inputs = 0

        prompt = (
            f"User was disatisfied with our results please, give them a nice short consise message telling them sorry and that we shall try again, mention that they should re enter input, maybe and some nice emoji"
        )
        message =  await gemini.send_user_message(prompt)
        
        if second_input == "":
            first_input = ""
        else:
            second_input = ""

    if not final:
        prompt = (
            f"User was happy with our results, please create a nice message like 2-3 sentances and include this part at the end:"
            f"Now list the proposed medications of your patient in the same format as before i.e: `Medicine_A, Medicine_B, Medicine_C, ..., Medicine_Z`.\n\n"
        )
        message = await gemini.send_user_message(prompt)
        user_inputs = user_inputs + 1
        final = True
    
    else:
        results = sparql.get_alternatives(first_input, second_input)
        #get infor

    
    await cl.Message(content=message).send()

async def parse_user_input(input):
    global user_inputs, first_input, second_input
    prompt = prompts.medicine_extraction_prompt(input)

    # Get response from Gemini and display it
    extracted_input = await gemini.send_user_message(prompt)
    clarifiying_output = (
        f"* **Patients current medications**: `{extracted_input}`\n\n"
        f"Does that look right? `Please answer yes or no`, keep in mind active substances does not equal brand names."
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

    print(user_inputs)

    if user_inputs % 2 == 0:
        await parse_user_input(input)
        return

    if user_inputs % 2 == 1:
        await user_satisfaction(input)
        return
