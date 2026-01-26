from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    with open("model_list.txt", "w") as f:
        paged_response = client.models.list()
        for model in paged_response:
            f.write(f"Name: {model.name} | Display: {model.display_name}\n")
    print("Model list written to model_list.txt")
except Exception as e:
    print(f"Error: {e}")
