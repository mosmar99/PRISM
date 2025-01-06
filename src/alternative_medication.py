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

    satisfied = await gemini.send_user_message(prompt)
    satisfied = satisfied.strip()

    message = ""

    if satisfied.strip() == "No":
        user_inputs = 0

        prompt = (
            f"User was disatisfied with our results please, give them a nice short consise message telling them sorry and that we shall try again, mention that they should re enter input, maybe and some nice emoji"
        )
        message =  await gemini.send_user_message(prompt)
        
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
        message = await gemini.send_user_message(prompt)
        user_inputs = user_inputs + 1
        final = True
        await cl.Message(content=message).send()
        return
    
    else:
        results = ""
        msg = await cl.Message(content="Thinking...").send()

        list = [item.strip() for item in first_input.split(',')]

        for medicine in list:
            results = results + sparql.get_alternatives(medicine, second_input)
        
        print(results)

        prompt = (
            "Below is a list of medications and substances. Identify the top 6 most common or popular legal alternatives "
            "from the list provided, ensuring that the alternatives align with the primary use case of the medication being replaced. "
            "At the top, include a note indicating that these are safe alternatives in the format: "
            "`Safe alternatives for: [medication_A] with regards to [medication_B]`. "
            "Consider the context of each medication's primary use case, such as pain relief, epilepsy, or sleep aid, "
            "to ensure the recommendations are relevant. If the list is empty, indicate that the interaction is safe by default. "
            "Example input format: "
            "`SAFE ALTERNATIVES FOR: Medicine A WITH REGARDS TO Medicine B, MEDICATION NAMES:`"
            "\n\n"
            f"{results}\n\n"
            "Output the safe alternative context first, followed by the 6 most appropriate and commonly used alternatives as a bullet list. "
            "If no alternatives are appropriate, state that explicitly "
            "Example 1:"
            "\nSafe alternatives for: `tramadol` with regards to `zopiclone`"
            "* Ibuprofen"
            "* Codeine"
            "* Aspirin"
            "* Naproxen"
            "* Diclofenac"
            "* Paracetamol"
            "\n"
            "Important: Avoid listing medications with unrelated primary use cases. For example, gabapentin (primarily used for epilepsy) "
            "should not be recommended as an alternative for tramadol (primarily used for pain relief) despite overlapping secondary use cases. "
            "Always focus on the primary indications when selecting alternatives."
            "ALWAYS INCLUDE THIS EXACT WARNING:"
            "General Healthcare Warning: Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice"
        )

        message = await gemini.send_user_message(prompt)
        msg.content = message
        await msg.update()
        final = "More"
        await show_buttons()

        return
    

async def parse_user_input(input):
    global user_inputs, first_input, second_input
    prompt = prompts.medicine_extraction_prompt(input)

    # Get response from Gemini and display it
    extracted_input = await gemini.send_user_message(prompt)
    clarifiying_output = (
        f"* **Patients current medications**: `{extracted_input}`\n\n"
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
        response = await gemini.send_user_message(input)
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
            name="query_again",
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

