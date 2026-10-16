import sqlite3
import time

from config import DATABASE_PATH, MAX_RESULT_ROWS
from sql.validate_sql import validate_sql


# Maximum time allowed for a SQL query
QUERY_TIMEOUT_SECONDS = 5


def execute_sql(sql):
    """Execute validated SQL safely using read-only SQLite."""

    # 1. Validate SQL
    valid, message = validate_sql(sql)

    if not valid:
        return {"error": message}

    # 2. Open database in read-only mode
    database_url = DATABASE_PATH.resolve().as_uri() + "?mode=ro"

    connection = sqlite3.connect(
        database_url,
        uri=True
    )

    try:

        # 3. Allow only read operations
        connection.execute("PRAGMA query_only = ON")

        # 4. Start query timer
        start_time = time.monotonic()

        # 5. Stop queries taking too long
        def check_query():

            elapsed = time.monotonic() - start_time

            if elapsed > QUERY_TIMEOUT_SECONDS:
                return 1

            return 0

        connection.set_progress_handler(check_query, 1000)

        # 6. Execute SQL
        cursor = connection.execute(sql)

        # 7. Get column names
        columns = [
            column[0]
            for column in cursor.description
        ]

        # 8. Fetch limited rows
        rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)

        # 9. Check if results were truncated
        truncated = len(rows) > MAX_RESULT_ROWS

        rows = rows[:MAX_RESULT_ROWS]

        # 10. Return results
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated
        }

    except sqlite3.OperationalError as error:

        if "interrupted" in str(error).lower():
            return {
                "error": (
                    f"Query exceeded the {QUERY_TIMEOUT_SECONDS}-second "
                    "execution limit."
                )
            }

        return {"error": str(error)}

    except sqlite3.Error as error:
        return {"error": str(error)}

    finally:
        connection.close()


# Test SQL execution
if __name__ == "__main__":

    sql = """
    SELECT COUNT(*) AS orders_without_review
    FROM orders o
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews r
        WHERE r.order_id = o.order_id
    );
    """

    print("Testing orders without reviews...")

    result = execute_sql(sql)

    if "error" in result:
        print("ERROR:", result["error"])

    else:
        print("RESULT:", result["rows"])