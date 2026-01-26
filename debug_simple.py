from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("--- Available Models ---")
    paged_response = client.models.list()
    for model in paged_response:
        print(f"Name: {model.name}")
        print(f"  Display: {model.display_name}")
except Exception as e:
    print(f"Error: {e}")
