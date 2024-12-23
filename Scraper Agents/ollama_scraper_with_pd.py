import pandas as pd
import requests
import json

# Load the CSV file
web_links = pd.read_csv("web_links.csv")

# Ensure all URLs start with 'https://' or 'http://'
web_links['URL'] = web_links['URL'].apply(lambda x: f"https://{x}" if not x.startswith(("http://", "https://")) else x)

# Define the Ollama API configuration
OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral"

# Loop through each URL and send requests to Ollama
for link in web_links['URL']:
    try:
        # Define the prompt
        prompt = f"Extract the description of the website {link} only. Then, summarise it concisely in one line. Output the summary only."
        
        # Create the payload
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Send the request to Ollama
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=120)

        # Accumulate response chunks
        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                try:
                    data = json.loads(chunk)
                    full_response += data.get("message", {}).get("content", "")
                except json.JSONDecodeError:
                    print(f"Non-JSON chunk: {chunk.decode('utf-8')}")
        
        # Print the reconstructed response
        print(f"Website: {link}")
        print(f"Summary: {full_response.strip()}")
        print("-" * 50)

    except Exception as e:
        # Handle errors (e.g., timeout, invalid response)
        print(f"Error processing {link}: {e}")
