import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

text_box = "debug"

try:
    client = genai.Client(api_key=api_key)
    print("Listing available models...")
    for model in client.models.list():
        print(f"Model: {model.name}")
        if "gemini" in model.name:
            print(f"  - Supported generation methods: {model.supported_generation_methods}")

    print("\nAttempting test generation with 'gemini-1.5-flash'...")
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Hello, are you there?'
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Test generation failed: {e}")

except Exception as e:
    print(f"Error initializing client or listing models: {e}")
