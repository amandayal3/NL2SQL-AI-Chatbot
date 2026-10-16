
import json

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, AIMessage

from config import METADATA_PATH
from classifier.jev_classifier import classify_intent
from conversation.followup_resolver import resolve_followup
from sql.generate_sql import generate_sql
from sql.validate_sql import validate_sql
from sql.execute_sql import execute_sql
from response.explain_results import explain_results


# 1. Enable real Groq AI
TEST_MODE = False


# 2. Define chatbot state
class ChatState(TypedDict):

    question: str
    intent: str
    answer: str
    resolved_question: str

    messages: Annotated[list, add_messages]

    # SQL query and results for Streamlit
    sql_query: str
    rows: list
    columns: list


# 3. Classify the user's question
def classify_node(state: ChatState):

    question = state["question"]

    if TEST_MODE:

        text = question.lower().strip()

        if text in ("hi", "hello", "hey"):
            intent = "chitchat"

        elif "table" in text or "column" in text:
            intent = "metadata_question"

        elif "what about" in text or "top 3" in text:
            intent = "follow_up"

        elif "customer" in text or "order" in text:
            intent = "data_question"

        else:
            intent = "out_of_scope"

    else:

        result = classify_intent(
            question,
            state.get("messages", [])
        )

        intent = result["intent"]

    return {"intent": intent}


# 4. Handle greetings
def chitchat_node(state: ChatState):

    return {
        "answer": (
            "Hello! Ask me anything about the "
            "e-commerce database."
        )
    }


# 5. Resolve follow-up questions
def followup_node(state: ChatState):

    question = state["question"]
    messages = state.get("messages", [])

    if not messages:

        return {
            "resolved_question": "CANNOT_RESOLVE",
            "answer": (
                "Please ask a complete question first "
                "so I can understand the follow-up."
            )
        }

    try:

        resolved = resolve_followup(
            question,
            messages
        )

    except Exception as error:

        print(
            "FOLLOW-UP ERROR:",
            type(error).__name__,
            str(error)
        )

        return {
            "resolved_question": "CANNOT_RESOLVE",
            "answer": (
                "Sorry, I could not understand "
                "the follow-up question."
            )
        }

    if not resolved or resolved.strip() == "CANNOT_RESOLVE":

        return {
            "resolved_question": "CANNOT_RESOLVE",
            "answer": (
                "Could you please explain your "
                "question in more detail?"
            )
        }

    return {
        "resolved_question": resolved.strip()
    }


# 6. Handle database questions
def data_node(state: ChatState):

    question = (
        state.get("resolved_question")
        or state["question"]
    )

    # Generate SQL
    if TEST_MODE:

        sql = """
        SELECT COUNT(DISTINCT customer_unique_id)
        AS total_customers
        FROM customers
        """

    else:

        try:

            sql = generate_sql(question)

        except Exception as error:

            print(
                "SQL GENERATION ERROR:",
                type(error).__name__,
                str(error)
            )

            return {
                "answer": (
                    "Sorry, I could not generate SQL right now."
                ),
                "sql_query": ""
            }

        if not sql or sql.strip() == "CANNOT_ANSWER":

            return {
                "answer": (
                    "Sorry, I cannot answer this "
                    "using the database."
                ),
                "sql_query": ""
            }

    print("\nGENERATED SQL:")
    print(sql)

    # Validate SQL
    try:

        validation = validate_sql(sql)

        if validation is False:

            return {
                "answer": (
                    "The generated SQL did not "
                    "pass validation."
                ),
                "sql_query": ""
            }

        if isinstance(validation, dict):

            if (
                validation.get("valid") is False
                or validation.get("is_valid") is False
            ):

                return {
                    "answer": (
                        "The generated SQL did not "
                        "pass validation."
                    ),
                    "sql_query": ""
                }

        if isinstance(validation, tuple):

            if validation[0] is False:

                return {
                    "answer": (
                        "The generated SQL did not "
                        "pass validation."
                    ),
                    "sql_query": ""
                }

        print("SQL VALIDATION PASSED")

    except Exception as error:

        print(
            "SQL VALIDATION ERROR:",
            type(error).__name__,
            str(error)
        )

        return {
            "answer": (
                "The generated SQL did not "
                "pass validation."
            ),
            "sql_query": ""
        }

    # Execute SQL
    try:

        result = execute_sql(sql)

    except Exception as error:

        print(
            "SQL EXECUTION ERROR:",
            type(error).__name__,
            str(error)
        )

        return {
            "answer": (
                "Sorry, the database query failed."
            ),
            "sql_query": ""
        }

    if "error" in result:

        print(
            "DATABASE ERROR:",
            result["error"]
        )

        return {
            "answer": (
                f"Database query failed: {result['error']}"
            ),
            "sql_query": ""
        }

    print(
        "DATABASE COLUMNS:",
        result["columns"]
    )

    print(
        "DATABASE ROWS:",
        result["rows"][:5]
    )

    # Explain SQL results
    if TEST_MODE:

        if result["rows"]:

            total = result["rows"][0][0]

            answer = (
                f"There are {total:,} unique "
                "customers in the database."
            )

        else:

            answer = "No customer data was found."

    else:

        try:

            answer = explain_results(
                question,
                result
            )

        except Exception as error:

            print(
                "RESULT EXPLANATION ERROR:",
                type(error).__name__,
                str(error)
            )

            answer = (
                "Sorry, I could not explain "
                "the results right now."
            )

    # Return answer, SQL query, and results
    return {
        "answer": answer,
        "sql_query": sql,
        "rows": result["rows"],
        "columns": result["columns"]
    }


# 7. Handle metadata questions
def metadata_node(state: ChatState):

    question = (
        state.get("resolved_question")
        or state["question"]
    ).lower()

    try:

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metadata = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):

        return {
            "answer": (
                "Sorry, I could not load "
                "the database metadata."
            )
        }

    tables = {
        name: details
        for name, details in metadata.items()
        if name not in (
            "relationships",
            "business_rules"
        )
    }

    if "how many tables" in question:

        return {
            "answer": (
                f"The database contains "
                f"{len(tables)} tables."
            )
        }

    if "column" in question:

        for table_name, details in tables.items():

            if table_name.lower() in question:

                column_names = [
                    column["name"]
                    for column in details.get(
                        "columns",
                        []
                    )
                ]

                return {
                    "answer": (
                        f"The {table_name} table "
                        "contains these columns: "
                        + ", ".join(column_names)
                    )
                }

        return {
            "answer": (
                "Please tell me which table's "
                "columns you want."
            )
        }

    if "table" in question:

        return {
            "answer": (
                f"The database contains "
                f"{len(tables)} tables: "
                + ", ".join(tables.keys())
                + "."
            )
        }

    return {
        "answer": (
            "Please ask about available tables "
            "or table columns."
        )
    }


# 8. Handle other intents
def other_node(state: ChatState):

    intent = state["intent"]

    if intent == "clarification":

        answer = (
            "Could you please explain your "
            "question in more detail?"
        )

    elif intent == "error":

        answer = (
            "The AI service is temporarily unavailable."
        )

    elif intent == "follow_up":

        answer = (
            "Please provide more details "
            "about your question."
        )

    else:

        answer = (
            "I can help you with questions "
            "about e-commerce data."
        )

    return {"answer": answer}


# 9. Save conversation history
def save_memory_node(state: ChatState):

    return {
        "messages": [
            HumanMessage(
                content=state["question"]
            ),
            AIMessage(
                content=state["answer"]
            )
        ]
    }


# 10. Route questions
def route_question(state: ChatState):

    intent = state["intent"]

    if intent in (
        "chitchat",
        "data_question",
        "metadata_question",
        "follow_up"
    ):

        return intent

    return "other"


# 11. Route resolved follow-ups
def route_followup(state: ChatState):

    resolved = state.get(
        "resolved_question",
        ""
    )

    if resolved == "CANNOT_RESOLVE":

        return "save_memory"

    text = resolved.lower()

    if "table" in text or "column" in text:

        return "metadata_question"

    return "data_question"


# 12. Build LangGraph
builder = StateGraph(ChatState)

builder.add_node(
    "classify",
    classify_node
)

builder.add_node(
    "chitchat",
    chitchat_node
)

builder.add_node(
    "follow_up",
    followup_node
)

builder.add_node(
    "data_question",
    data_node
)

builder.add_node(
    "metadata_question",
    metadata_node
)

builder.add_node(
    "other",
    other_node
)

builder.add_node(
    "save_memory",
    save_memory_node
)

builder.add_edge(
    START,
    "classify"
)

builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "chitchat": "chitchat",
        "data_question": "data_question",
        "metadata_question": "metadata_question",
        "follow_up": "follow_up",
        "other": "other"
    }
)

builder.add_conditional_edges(
    "follow_up",
    route_followup,
    {
        "data_question": "data_question",
        "metadata_question": "metadata_question",
        "save_memory": "save_memory"
    }
)

builder.add_edge(
    "chitchat",
    "save_memory"
)

builder.add_edge(
    "data_question",
    "save_memory"
)

builder.add_edge(
    "metadata_question",
    "save_memory"
)

builder.add_edge(
    "other",
    "save_memory"
)

builder.add_edge(
    "save_memory",
    END
)


# 13. Enable conversation memory
memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# 14. Test multiple questions
if __name__ == "__main__":

    print(
        "LangGraph Follow-up Debug Test Started"
    )

    config = {
        "configurable": {
            "thread_id": "test_user_1"
        }
    }

    questions = [
        "Which 5 states have the most customers?",
        "What about the top 10?",
        "Show only the top 3.",
        "How many orders are there?",
        "What about delivered orders?"
    ]

    for question in questions:

        result = graph.invoke(
            {
                "question": question,
                "intent": "",
                "answer": "",
                "resolved_question": "",
                "sql_query": "",
                "rows": [],
                "columns": []
            },
            config=config
        )

        print("\n" + "=" * 50)

        print(
            "USER:",
            question
        )

        print(
            "INTENT:",
            result["intent"]
        )

        if result["intent"] == "follow_up":

            print(
                "RESOLVED:",
                result["resolved_question"]
            )

        print(
            "CHATBOT:",
            result["answer"]
        )

        if result.get("sql_query"):

            print(
                "SQL QUERY:",
                result["sql_query"]
            )

        print(
            "MESSAGES STORED:",
            len(result["messages"])
        )

        if result.get("rows"):

            print(
                "RESULT COLUMNS:",
                result["columns"]
            )

            print(
                "RESULT ROWS:",
                result["rows"][:5]
            )

    print(
        "\nLangGraph Follow-up Debug Test Completed!"
    )
