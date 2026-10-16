from llm.groq_client import ask_llm


def explain_results(question, result):

    # Check database errors
    if "error" in result:
        return f"Database error: {result['error']}"

    # Check empty results
    if not result["rows"]:
        return "No matching data was found."

    # Limit data sent to Groq
    MAX_EXPLANATION_ROWS = 10

    rows = result["rows"][:MAX_EXPLANATION_ROWS]

    system_prompt = """
    You are an e-commerce data analyst.

    Explain database results in simple English.

    Rules:
    1. Answer the question directly.
    2. Use only the provided results.
    3. Never invent numbers.
    4. Keep the answer short.
    5. Use commas for large numbers.
    6. Do not claim the sample contains all results.
    7. If the data is incomplete, mention that.
    """

    prompt = f"""
    Question:
    {question}

    Columns:
    {result['columns']}

    Sample Rows:
    {rows}

    Total Rows Returned:
    {result['row_count']}

    Results Truncated:
    {result.get('truncated', False)}

    Rows Sent for Explanation:
    {len(rows)}

    Explain the results in simple English.
    """

    answer = ask_llm(
        prompt=prompt,
        system_prompt=system_prompt
    )

    return answer.strip()


if __name__ == "__main__":

    question = "How many delivered orders are there?"

    result = {
        "columns": ["delivered_orders"],
        "rows": [(96478,)],
        "row_count": 1,
        "truncated": False
    }

    answer = explain_results(question, result)

    print("Question:", question)
    print("Answer:", answer)