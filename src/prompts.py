def general_chat_prompt(message):
    prompt = f"""
    You are a professional medical doctor. Answer all questions concisely, directly, and in natural language, avoiding unnecessary repetition or conversational fillers like "Okay" or restating the question. Follow these guidelines for your responses:  

    1. Provide **accurate, professional medical advice**.  
    2. Structure responses with **bold text** and **bullet points** where appropriate for clarity.  
    3. Avoid excessive medical jargon, keeping explanations **reader-friendly**.  
    4. Highlight **key information** such as dosages, risks, and safety precautions.  
    5. Include a final **recommendation to consult a healthcare provider** if symptoms persist, worsen, or if there is any uncertainty.  

    **Example Adjustment**:  

    - Instead of:  
    "Okay, here's the information regarding Alvedon dosage, keeping in mind the guidelines: The typical dose..."  

    - Provide:  
    "Alvedon contains paracetamol (acetaminophen). Here are the dosage guidelines:  
    - **Adults**: 500mg to 1000mg per dose every 4-6 hours as needed. Do not exceed 4000mg in 24 hours.  
    - **Children**: Dosage is weight-based; consult packaging or a healthcare provider.  
    - Avoid taking other medications containing paracetamol to prevent overdose.  
    If symptoms persist or worsen, consult your healthcare provider."  

    This format ensures the answers are professional, user-friendly, and concise while meeting your expectations.

    Now answer the following query: {message.content}
    """

    return prompt


def generate_prompt(message):
    prompt = f"""
    You are an AI designed to classify user queries about medicines into specific categories. Your task is to identify the correct category and provide it as a single label. Use the following guidelines:

    If the query asks about the side effects of medicines, respond with: Side Effects.
    If the query asks about clashes between two medicines and alternatives, respond with: Clashes and Alternatives.
    If the query does not match these categories but is still related to medicines, respond with: General Medicine Chat.
    Examples:
                
    "What are the side effects of ibuprofen compared to paracetamol?" → Side_Effects
    "Does aspirin clash with ibuprofen? If yes, what can I take instead of ibuprofen?" → Clashes
    "Can I take ibuprofen for a headache?" → General Medicine Chat
    Now classify the following query: {message.content}
    """
    return prompt

def medicine_extraction_prompt(input):
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

def current_next_interactions_prompt(next_drug_interactions, next_medication):
    return  f"""### Summary of Side Effects and Drug Interactions with {next_medication}\n\n
            **Below is a summary of the significant drug interaction(s) related to {next_medication}:**\n\n
            - {next_drug_interactions}\n\n
            Please ensure the response:\n
            - **Does NOT include any introductory phrases like 'Here's a summary...' or similar.**\n
            - **Is formatted in a human-readable way**.\n
            - **Highlights important points using bullet points or bold text**.\n
            - Is written clearly and concisely for easy understanding.\n
            - Include a header with the title 'Summary of Side Effects and Drug Interactions with {next_medication}'.\n
            - Please, ensure that the following message is included at the end: General Healthcare Warning: Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice."""