from dotenv import load_dotenv
import os

import openai

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("LLAMA_API")
url = os.getenv("LLAMA_URL")

client = openai.Client(api_key=api_key, base_url=url)

print("hi i have found the client")

try:
    res = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",  # Updated to match available model
        messages=[
            {
                "content": "Who is Pablo Picasso?",
                "role": "user",
            }
        ],
        stream=True,
    )

    for chunk in res:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

except Exception as e:
    print(f"Completion error: {str(e)}")
    print(f"Error type: {type(e)}")