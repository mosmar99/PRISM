import prompts
import gemini
import sparql
import chainlit as cl


# patients current medication -> proposed new medication

async def chat_start():
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


async def extraction(message: cl.Message):
    input = message.content
    if(input.len() <= 1):
        return

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
