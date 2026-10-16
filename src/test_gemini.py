from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

# Check API key
if not GEMINI_API_KEY:
    print("Gemini API key is missing!")

else:
    # Connect to Gemini
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Ask Gemini a simple question
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents="Say hello in one short sentence."
    )

    # Print Gemini's answer
    print("Gemini Response:")
    print(response.text)