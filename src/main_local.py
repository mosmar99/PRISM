import chainlit as cl
import ollama

@cl.on_message
async def main(message):
    """
    This function is triggered whenever a user sends a message in the Chainlit interface.
    """
    try:
        # Query the local Ollama model
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': message.content}]
        )
        
        # Extract the content from the response
        response_text = response['message']['content']

        # Send the response back to the Chainlit interface
        await cl.Message(content=response_text).send()
    except Exception as e:
        # Send an error message to the Chainlit interface in case of issues
        await cl.Message(content=f"Error: {str(e)}").send()
