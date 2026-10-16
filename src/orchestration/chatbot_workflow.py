import json
import time

from google import genai
from google.genai import types, errors

from config import GEMINI_API_KEY, GEMINI_MODEL


# Connect to Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


def classify_intent(question):
    """Identify the user's intent."""

    prompt = f"""
You are JEV, an intent classifier for an e-commerce
database chatbot.

Classify the user's message into exactly one intent.

Available intents:

1. chitchat
   Greetings, thanks, or casual conversation.

2. data_question
   Questions requiring information from the database.

3. metadata_question
   Questions about database tables, columns, or structure.

4. follow_up
   Questions referring to an earlier conversation.

5. clarification
   Questions that are unclear or incomplete.

6. out_of_scope
   Requests unrelated to the e-commerce database
   or basic conversation.

Rules:
- Return only a JSON object.
- Use exactly one intent.
- Keep the reason short.
- Do not generate SQL.
- If there is no conversation history, do not assume
  that an unclear question refers to a previous message.

USER MESSAGE:
{question}

Return JSON in this format:
{{
    "intent": "data_question",
    "reason": "The user wants information from the database."
}}
"""

    allowed_intents = {
        "chitchat",
        "data_question",
        "metadata_question",
        "follow_up",
        "clarification",
        "out_of_scope"
    }

    # Try up to 3 times if Gemini is temporarily busy
    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            # Convert Gemini response into a dictionary
            result = json.loads(response.text)

            # Check whether the response is valid
            if not isinstance(result, dict):
                return {
                    "intent": "error",
                    "reason": "Gemini returned an invalid response."
                }

            # Check the detected intent
            if result.get("intent") not in allowed_intents:
                return {
                    "intent": "error",
                    "reason": "Gemini returned an unknown intent."
                }

            return {
                "intent": result["intent"],
                "reason": result.get("reason", "")
            }

        # Handle Gemini API errors
        except errors.APIError as error:

            # Get the HTTP error code
            status_code = getattr(error, "code", None)

            # Quota exceeded
            if status_code == 429:
                return {
                    "intent": "error",
                    "reason": (
                        "Gemini API quota exceeded. "
                        "Please try again after the quota resets."
                    )
                }

            # Temporary server error
            if status_code in (500, 502, 503, 504):

                print("Gemini is busy. Trying again...")

                if attempt < 2:
                    time.sleep(5)
                    continue

                return {
                    "intent": "error",
                    "reason": "Gemini is temporarily unavailable."
                }

            # Other API errors
            return {
                "intent": "error",
                "reason": f"Gemini API error: {status_code}"
            }

        # Handle invalid JSON
        except (json.JSONDecodeError, TypeError):
            return {
                "intent": "error",
                "reason": "Gemini returned invalid JSON."
            }

    return {
        "intent": "error",
        "reason": "Could not classify the question."
    }


# Test the classifier
if __name__ == "__main__":

    questions = [
        "Hi",
        "How many customers are there?",
        "What tables are available?",
        "Show the same for last year",
        "Which state?",
        "Write a poem about love"
    ]

    for question in questions:

        result = classify_intent(question)

        print("\nQuestion:", question)
        print("Intent:", result["intent"])
        print("Reason:", result["reason"])
        print("-" * 50)

        # Stop if Gemini is unavailable
        if result["intent"] == "error":
            break