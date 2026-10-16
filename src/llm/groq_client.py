from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


# Step 1: Connect to Groq
client = Groq(api_key=GROQ_API_KEY)


# Step 2: Reusable LLM function
def ask_llm(prompt, system_prompt=None):

    messages = []

    # Add system instructions
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    # Add user's prompt
    messages.append({
        "role": "user",
        "content": prompt
    })

    # Step 3: Call Groq API
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0
    )

    # Step 4: Display token usage
    if response.usage:

        print("\n--- GROQ TOKEN USAGE ---")

        print(
            "Input tokens:",
            response.usage.prompt_tokens
        )

        print(
            "Output tokens:",
            response.usage.completion_tokens
        )

        print(
            "Total tokens:",
            response.usage.total_tokens
        )

        print("------------------------")

    # Step 5: Return generated text
    return response.choices[0].message.content


# Step 6: Test Groq connection
if __name__ == "__main__":

    answer = ask_llm(
        prompt="What is a primary key in SQL? Explain in one sentence."
    )

    print("\nModel:", GROQ_MODEL)
    print("Answer:", answer)