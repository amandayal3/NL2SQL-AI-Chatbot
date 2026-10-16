from sql.generate_sql import generate_sql
from sql.validate_sql import validate_sql
from sql.execute_sql import execute_sql


# Step 1: Questions and expected answers

TEST_CASES = [
    {
        "question": "Which 3 sellers generated the highest item revenue? Show seller IDs and states.",
        "expected": [
            "4869f7a5",
            "53243585",
            "4a3ca931"
        ],
        "type": "seller_prefixes"
    },
    {
        "question": "What is the average review score for late deliveries?",
        "expected": 2.57,
        "type": "decimal"
    },
    {
        "question": "What is the average review score for on-time deliveries?",
        "expected": 4.29,
        "type": "decimal"
    },
    {
        "question": "How many orders have no review?",
        "expected": 768,
        "type": "number"
    },
    {
        "question": "What is the profit margin per product?",
        "expected": "CANNOT_ANSWER",
        "type": "refusal"
    }
]


# Step 2: Check SQL validation

def sql_is_valid(validation):

    if isinstance(validation, bool):
        return validation

    if isinstance(validation, dict):

        if "valid" in validation:
            return validation["valid"] is True

        if "is_valid" in validation:
            return validation["is_valid"] is True

    if isinstance(validation, tuple) and validation:
        return validation[0] is True

    return False


# Step 3: Compare actual results with expected results

def compare_results(test, rows):

    test_type = test["type"]
    expected = test["expected"]

    # Exact number comparison
    if test_type == "number":

        actual = rows[0][0]

        return actual == expected

    # Decimal comparison
    elif test_type == "decimal":

        actual = rows[0][0]

        return (
            isinstance(actual, (int, float))
            and abs(actual - expected) <= 0.01
        )

    # Ordered list comparison
    elif test_type == "ordered_list":

        actual = [row[0] for row in rows]

        return actual == expected

    # Unordered list comparison
    elif test_type == "unordered_list":

        actual = [row[0] for row in rows]

        return (
            len(actual) == len(expected)
            and set(actual) == set(expected)
        )

    # Seller ID comparison
    elif test_type == "seller_prefixes":

        actual = [
            str(row[0])[:8]
            for row in rows
        ]

        return actual == expected

    # Ranked city/count comparison
    elif test_type == "ranked_counts":

        actual_names = [row[0] for row in rows]
        actual_counts = [row[1] for row in rows]

        return (
            actual_names == expected
            and actual_counts == test["expected_values"]
        )

    return False


# Step 4: Test one question

def test_pipeline(test):

    question = test["question"]
    expected = test["expected"]
    test_type = test["type"]

    print("\n" + "=" * 60)
    print("QUESTION:", question)
    print("EXPECTED:", expected)

    try:

        # Generate SQL
        sql = generate_sql(question).strip()

        print("\nGENERATED SQL:")
        print(sql)

        # Handle questions without available data
        if sql == "CANNOT_ANSWER":

            passed = test_type == "refusal"

            print(
                "RESULT:",
                "PASS" if passed else "FAIL"
            )

            return passed

        # A refusal was expected, but SQL was generated
        if test_type == "refusal":

            print("RESULT: FAIL — expected CANNOT_ANSWER")

            return False

        # Validate SQL
        validation = validate_sql(sql)

        print("\nVALIDATION:")
        print(validation)

        if not sql_is_valid(validation):

            print("RESULT: FAIL — SQL validation failed")

            return False

        # Execute SQL
        result = execute_sql(sql)

        if "error" in result:

            print("DATABASE ERROR:", result["error"])
            print("RESULT: FAIL")

            return False

        rows = result["rows"]

        print("\nDATABASE RESULT:")

        for row in rows[:10]:
            print(row)

        # Check empty results
        if not rows:

            print("RESULT: FAIL — no rows returned")

            return False

        # Check truncated results
        if result.get("truncated"):

            print("RESULT: FAIL — result was truncated")

            return False

        # Compare answers
        passed = compare_results(test, rows)

        print(
            "\nRESULT:",
            "PASS" if passed else "FAIL"
        )

        return passed

    except Exception as error:

        print(
            "ERROR:",
            type(error).__name__,
            str(error)
        )

        print("RESULT: FAIL")

        return False


# Step 5: Run all tests

if __name__ == "__main__":

    print("NL2SQL Pipeline Accuracy Test Started")

    passed = 0
    total = len(TEST_CASES)

    for test in TEST_CASES:

        if test_pipeline(test):
            passed += 1

    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")

    print("PASSED:", passed)
    print("FAILED:", total - passed)
    print("TOTAL:", total)

    if total > 0:

        accuracy = passed / total * 100

        print(
            "ACCURACY:",
            f"{accuracy:.1f}%"
        )