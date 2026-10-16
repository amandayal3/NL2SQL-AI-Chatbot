from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, AIMessage


# Step 1: Define conversation memory
class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]


# Step 2: Create chatbot function
def chatbot_node(state: MemoryState):

    # Get all conversation messages
    messages = state["messages"]

    # Get the latest user message
    last_message = messages[-1].content

    # Handle greetings
    if last_message.lower() == "hi":

        answer = "Hello! How can I help you?"

    # Check conversation memory
    elif "remember" in last_message.lower():

        answer = (
            f"I remember {len(messages)} messages "
            "in this conversation."
        )

    else:

        answer = "I received your message."

    # Return chatbot response
    return {
        "messages": [AIMessage(content=answer)]
    }


# Step 3: Build LangGraph
builder = StateGraph(MemoryState)

builder.add_node("chatbot", chatbot_node)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


# Step 4: Add conversation memory
memory = MemorySaver()

graph = builder.compile(checkpointer=memory)


# Step 5: Test conversation memory
if __name__ == "__main__":

    print("Memory test started")

    # Same thread ID keeps conversation history
    config = {
        "configurable": {
            "thread_id": "test_user_1"
        }
    }

    # Test questions
    questions = [
        "Hi",
        "How many customers are there?",
        "Do you remember our conversation?"
    ]

    # Ask questions one by one
    for question in questions:

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            },
            config=config
        )

        print("\nUSER:", question)

        print(
            "CHATBOT:",
            result["messages"][-1].content
        )

    print("\nMemory test completed!")