import sqlglot
from sqlglot import exp


# Tables that our chatbot can access
ALLOWED_TABLES = {
    "orders",
    "customers",
    "order_items",
    "products",
    "sellers",
    "payments",
    "reviews",
    "geolocation",
    "category_translation"
}


def validate_sql(sql):
    """Allow safe, read-only SELECT queries, including CTEs."""

    try:
        # 1. Parse SQL
        statements = sqlglot.parse(sql, read="sqlite")

        if len(statements) != 1 or statements[0] is None:
            return False, "Only one SQL query is allowed."

        query = statements[0]

        # 2. Allow SELECT queries only
        if not isinstance(query, exp.Select):
            return False, "Only SELECT queries are allowed."

        # 3. Block unsafe operations
        blocked_types = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Command,
            exp.Attach,
            exp.Pragma,
        )

        for node in query.walk():
            if isinstance(node, blocked_types):
                return False, "Unsafe SQL operation detected."

        # 4. Collect CTE names
        cte_names = set()

        for cte in query.find_all(exp.CTE):
            cte_names.add(cte.alias.lower())

            # A CTE must also contain a SELECT query
            if not isinstance(cte.this, exp.Select):
                return False, "Only SELECT queries are allowed inside CTEs."

        # 5. Check SELECT expressions
        for select in query.find_all(exp.Select):
            if not select.expressions:
                return False, "SELECT must contain columns."

        # 6. Check table names
        for table in query.find_all(exp.Table):

            table_name = table.name.lower()

            # Allow real database tables
            if table_name in ALLOWED_TABLES:
                continue

            # Allow CTE references
            if table_name in cte_names:
                continue

            return False, f"Table not allowed: {table_name}"

        return True, "SQL validation passed."

    except Exception as error:
        return False, f"Invalid SQL: {error}"


# 7. Test validation
if __name__ == "__main__":

    queries = [
        # Safe queries
        "SELECT * FROM customers LIMIT 5;",
        "SELECT COUNT(*) FROM orders;",

        # Safe CTE
        """
        WITH total AS (
            SELECT SUM(price) AS revenue
            FROM order_items
        )
        SELECT revenue FROM total;
        """,

        # Invalid table
        "SELECT * FROM sqlite_master;",

        # Unsafe operations
        "DELETE FROM customers;",
        "DROP TABLE orders;",
        "UPDATE reviews SET review_score = 5;",

        # Invalid CTE
        """
        WITH secret AS (
            SELECT * FROM sqlite_master
        )
        SELECT * FROM secret;
        """,

        # Multiple statements
        "SELECT * FROM orders; DROP TABLE orders;"
    ]

    for sql in queries:

        valid, message = validate_sql(sql)

        print("\nSQL:", sql.strip())
        print("Valid:", valid)
        print("Message:", message)