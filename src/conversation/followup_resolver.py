from llm.groq_client import ask_llm
from langchain_core.messages import HumanMessage, AIMessage


def resolve_followup(question, messages):

    # No previous conversation
    if not messages:
        return question

    # Keep the last 6 messages
    recent_messages = messages[-6:]

    history = ""

    for message in recent_messages:

        if isinstance(message, HumanMessage):
            history += f"User: {message.content}\n"

        elif isinstance(message, AIMessage):
            history += f"Assistant: {message.content}\n"

    system_prompt = """
    You rewrite follow-up questions for an e-commerce database chatbot.

    Use the previous conversation to understand the new question.

    Rules:
    1. Rewrite the question into a complete, standalone question.
    2. Keep the user's original meaning.
    3. Preserve the previous topic, filters, and metrics unless changed.
    4. Do not answer the question.
    5. Do not generate SQL.
    6. Return only the rewritten question.
    7. If the question is unclear, return CANNOT_RESOLVE.
    """

    prompt = f"""
    Previous Conversation:
    {history}

    New Question:
    {question}

    Rewrite the new question.
    """

    answer = ask_llm(
        prompt=prompt,
        system_prompt=system_prompt
    )

    return answer.strip()


# Test
if __name__ == "__main__":

    messages = [
        HumanMessage(
            content="Which 5 states have the most customers?"
        ),
        AIMessage(
            content="SP, RJ, MG, RS and PR have the most customers."
        )
    ]

    question = "What about the top 10?"

    result = resolve_followup(question, messages)

    print("Original Question:", question)
    print("Resolved Question:", result)