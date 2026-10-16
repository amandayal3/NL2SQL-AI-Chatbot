from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

response = client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {
            "role": "user",
            "content": "What is SQL? Explain in one simple sentence."
        }
    ],
    temperature=0
)

print("Model:", GROQ_MODEL)
print("Response:", response.choices[0].message.content)