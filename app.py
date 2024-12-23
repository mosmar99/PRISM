import requests

# Define the endpoint URL
url = "http://localhost:11434"  # Adjust the port if necessary

def send_message(message):
    # Create the payload
    payload = {
        "input": message
    }
    
    # Send a POST request to the Ollama model
    response = requests.post(url, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    # Message to send
    user_input = "hello llama, how are you?"
    
    # Send the message and get the response
    response = send_message(user_input)
    
    # Print the response
    if response:
        print("Response from model:", response)
