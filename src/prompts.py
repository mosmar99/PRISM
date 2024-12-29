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