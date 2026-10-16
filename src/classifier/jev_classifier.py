import json

from llm.groq_client import ask_llm


# Valid chatbot intents
VALID_INTENTS = [
    "chitchat",
    "data_question",
    "metadata_question",
    "follow_up",
    "clarification",
    "out_of_scope"
]


def classify_intent(question, messages=None):

    # Get previous conversation
    history = []

    if messages:
        for message in messages[-6:]:
            role = "User" if message.type == "human" else "Assistant"
            history.append(f"{role}: {message.content}")

    conversation = "\n".join(history)

    system_prompt = """
    You are an intent classifier for an e-commerce SQL chatbot.

    Classify the latest user question into exactly one category.

    Categories:

    chitchat:
    Greetings, hello, thanks.

    data_question:
    A new, complete question that requires a SQL query.

    metadata_question:
    Questions about database tables, columns, or structure.

    follow_up:
    A question that refers to a previous question or answer.

    Examples:
    Previous: Which 5 states have the most customers?
    Current: What about the top 10?
    Intent: follow_up

    Previous: Which 10 states have the most customers?
    Current: Show only the top 3.
    Intent: follow_up

    Previous: How many orders are there?
    Current: What about delivered orders?
    Intent: follow_up

    clarification:
    An unclear question that cannot be understood even
    with conversation history.

    out_of_scope:
    Questions unrelated to the e-commerce database.

    Important rules:
    1. Use conversation history to understand the latest question.
    2. If the latest question modifies a previous question,
       classify it as follow_up.
    3. A complete new question is data_question.
    4. Do not classify a clear follow-up as clarification.
    5. If no relevant previous conversation exists,
       do not invent context.

    Return only valid JSON:

    {"intent": "follow_up"}

    Do not include explanations or markdown.
    """

    prompt = f"""
    Previous conversation:
    {conversation if conversation else "No previous conversation"}

    Latest user question:
    {question}

    Classify the latest user question.
    """

    try:

        response = ask_llm(
            prompt=prompt,
            system_prompt=system_prompt
        )

        response = response.strip()
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        result = json.loads(response)

        intent = result.get("intent", "clarification")

        if intent not in VALID_INTENTS:
            intent = "clarification"

        return {
            "intent": intent
        }

    except Exception as error:

        return {
            "intent": "error",
            "reason": str(error)
        }


# Test classifier
if __name__ == "__main__":

    from langchain_core.messages import HumanMessage, AIMessage

    messages = [
        HumanMessage(content="Which 5 states have the most customers?"),
        AIMessage(content="SP, RJ, MG, RS and PR are the top five states."),
        HumanMessage(content="What about the top 10?"),
        AIMessage(content="Here are the top ten states.")
    ]

    questions = [
        "Show only the top 3.",
        "How many orders are there?",
        "Hi"
    ]

    for question in questions:

        result = classify_intent(question, messages)

        print("\nQuestion:", question)
        print("Intent:", result["intent"])