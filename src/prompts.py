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

def user_satisfaction_prompt(input):
    return f"""
        You are an AI designed to assess user satisfaction based on their response. Your task is to determine whether the user is satisfied with the result. If the user expresses satisfaction or agreement, respond with: Yes. If the user expresses dissatisfaction, disagreement, or asks for improvements, respond with: No.

        Examples:

        "This is exactly what I needed, thank you!" → Yes
        "This doesn't help at all, can you try something else?" → No
        "It's okay, but could you refine it further?" → No
        "Perfect, this works great!" → Yes
        Now analyze the following response: {input}
    """
def symptoms_convert_to_latin(input):
    return f"""You are an AI assistant specialized in translating symptoms in USER_INPUT from english to latin.
    
    Example translation: 
    Input: ["shoulder inflammation", "joint inflammation", "lung inflammation"].
    Output: ["bursitis", "arthritis", "pneumonitis"].

    Maintain relative position of symptoms as found in USER_INPUT.
    Return the names as a comma-separated list.

    USER_INPUT: {input}"""

def symptoms_extraction_prompt(input):
    return f"""You are an AI assistant specialized in identifying and extracting symptoms from user text. Given any input, your task is to return only the names of symptoms mentioned in the text, correcting minor misspellings or variations if necessary. Follow these rules:

    Identify and extract symptom names (e.g., headache, fever, nausea).
    Correct minor misspellings or variations in the names of symptoms if they are clearly identifiable (e.g., "headach" should be "headache").
    Do not include descriptions, instructions, or dosages unless explicitly part of the symptom name.
    If no identifiable symptoms are mentioned, respond with "No symptoms mentioned."
    Do not infer or guess names that are ambiguous or not clearly indicated.
    maintain relative position of symptioms as listed in input.
    Return the names as a comma-separated list.
    Examples:

    Input: "I have a headache and fever." Output: "headache, fever"

    Input: "I feel nauseous and dizzy." Output: "nausea, dizziness"

    Input: "My stomach hurts and I have a fever." Output: "stomach pain, fever"

    Input: "I have a headache." Output: "headache"

    Input: "I feel unwell." Output: "No symptoms mentioned"

    Now, extract the symptoms from this input:

    USER_INPUT: {input}"""

def symptoms_med_recommendation_prompt(symptom_to_medications):
    return f"""
    ### Symptom and Medication Summary
 
    Please extract the relevant symptoms from the provided dictionary and format the output as follows:
    - For each symptom identified, provide a highlighted section for the symptom name.
    - List up to **three most commonly used medications** (at least one if it exists) associated with the symptom from the provided dictionary and is a legally prescribed substance.
    - Ensure the information is formatted clearly, using bullet points or concise descriptions.
    - Include a **General Healthcare Warning** at the end of the response, ensure double new line.
    - Include a header similar to "Recommended Medications given Symptoms".
    - Capitalize first letter in symptom name on output.
 
    Example Output Format:
    #### **Symptom Name**
 
    - Most commonly used medications: Medication1, Medication2, Medication3
    **General Healthcare Warning:** Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice.
 
    **Provided Dictionary**: {symptom_to_medications}
    """


def alt_med_summary_prompt(input):
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
            f"{input}\n\n"
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
            "MAKE SURE YOU INCLUDE ALL INPUTS:"
            "ALWAYS INCLUDE THIS EXACT WARNING:"
            "General Healthcare Warning: Always consult with a healthcare professional before taking any medication, including those mentioned above. This information is not a substitute for professional medical advice"
        )
    return prompt