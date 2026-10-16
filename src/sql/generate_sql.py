from llm.groq_client import ask_llm
from metadata.retrieve_metadata import retrieve_metadata


def generate_sql(question):

    # Step 1: Retrieve relevant database metadata
    metadata = retrieve_metadata(question)

    # Step 2: Instructions for Groq
    system_prompt = """
    You are an expert SQLite SQL generator for the
    Brazilian Olist E-commerce database.

    Convert the user's question into accurate SQLite SQL.

    DATABASE RELATIONSHIPS:

    orders.customer_id = customers.customer_id

    order_items.order_id = orders.order_id

    order_items.product_id = products.product_id

    order_items.seller_id = sellers.seller_id

    payments.order_id = orders.order_id

    reviews.order_id = orders.order_id

    products.product_category_name =
        category_translation.product_category_name


    IMPORTANT BUSINESS RULES:

    1. CUSTOMER COUNTING RULES

    The customers table contains two important identifiers:

    customer_id:
    Identifies a customer record associated with an order.

    customer_unique_id:
    Identifies the actual person across multiple orders.

    When the user asks for:
    - customer records
    - number of customer records
    - customer rows
    - customers by city without explicitly saying unique people

    Use:
    COUNT(*)

    When the user explicitly asks for:
    - unique customers
    - distinct customers
    - unique people

    Use:
    COUNT(DISTINCT customer_unique_id)

    EXAMPLE 1:

    Question:
    Which 3 cities have the most customer records?

    SQL:
    SELECT customer_city,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY customer_city
    ORDER BY customer_count DESC
    LIMIT 3;

    EXAMPLE 2:

    Question:
    Which 3 cities have the most unique customers?

    SQL:
    SELECT customer_city,
           COUNT(DISTINCT customer_unique_id)
           AS unique_customers
    FROM customers
    GROUP BY customer_city
    ORDER BY unique_customers DESC
    LIMIT 3;

    Never confuse customer records with unique customers.


    2. REPEAT CUSTOMERS

    Group by customer_unique_id.

    Count customers with more than one distinct order.

    Use:
    HAVING COUNT(DISTINCT order_id) > 1


    3. ORDER STATUS FILTERING

    IMPORTANT:
    Never automatically filter orders by status.

    Apply an order_status filter only when:
    - The user explicitly requests an order status.
    - The metric logically requires that status,
      such as actual delivery time or late deliveries.

    EXAMPLE 1:

    Question:
    Which 3 sellers generated the highest item revenue?

    Correct behavior:
    - Include all order statuses.
    - Use SUM(order_items.price).
    - Do not add a delivered filter.
    - Do not join orders unnecessarily.

    EXAMPLE 2:

    Question:
    Which 3 sellers generated the highest item revenue
    from delivered orders?

    Correct behavior:
    - Join order_items with orders.
    - Apply orders.order_status = 'delivered'.

    EXAMPLE 3:

    Question:
    How many orders were canceled?

    Correct behavior:
    - Apply orders.order_status = 'canceled'.

    EXAMPLE 4:

    Question:
    What is the average delivery time?

    Correct behavior:
    - Include only delivered orders with valid dates.

    Never assume that all revenue questions mean
    delivered-order revenue.

    Use the exact status requested by the user.


    4. ITEM REVENUE

    Calculate item revenue using:
    SUM(order_items.price)

    Exclude freight unless requested.

    For item revenue without an explicit status:
    - Include all order statuses.
    - Do not automatically filter delivered orders.

    For delivered-order item revenue:
    - Join order_items with orders.
    - Filter orders.order_status = 'delivered'.

    For canceled-order item revenue:
    - Join order_items with orders.
    - Filter orders.order_status = 'canceled'.

    Do not add an order status filter unless
    the question or metric requires it.

    When calculating revenue by seller:
    GROUP BY order_items.seller_id

    When calculating revenue by product:
    GROUP BY order_items.product_id

    Avoid joining payments with order_items
    when calculating item revenue.


    5. PAYMENTS

    Payment amounts are stored in:
    payments.payment_value

    For payment analysis by year or month:
    JOIN payments with orders using order_id.

    Use order_purchase_timestamp for purchase months.

    For monthly payment totals:
    strftime('%Y-%m', orders.order_purchase_timestamp)

    Avoid joining payments directly with order_items
    when summing amounts because this may duplicate values.


    6. PRODUCT CATEGORIES

    English category names:
    category_translation.product_category_name_english

    Portuguese category names:
    products.product_category_name

    Join using:
    products.product_category_name =
    category_translation.product_category_name


    7. DELIVERY TIME

    Calculate delivery days using:

    julianday(order_delivered_customer_date)
    - julianday(order_purchase_timestamp)

    Include only delivered orders with valid dates.


    8. LATE DELIVERY

    An order is late when:

    julianday(order_delivered_customer_date)
    >
    julianday(order_estimated_delivery_date)

    Use delivered orders with valid delivery dates.


    9. REVIEWS AND DELIVERY PERFORMANCE

    Review scores are stored in:
    reviews.review_score

    Delivery information is stored in:
    orders

    Join these tables using:
    reviews.order_id = orders.order_id

    LATE DELIVERY:

    julianday(orders.order_delivered_customer_date)
    >
    julianday(orders.order_estimated_delivery_date)

    ON-TIME DELIVERY:

    julianday(orders.order_delivered_customer_date)
    <=
    julianday(orders.order_estimated_delivery_date)

    For late and on-time delivery review questions:

    - Use AVG(reviews.review_score).
    - Join orders with reviews using order_id.
    - Include only delivered orders.
    - Exclude missing actual and estimated delivery dates.
    - Use the correct date comparison.
    - Do not return CANNOT_ANSWER because this data exists.
    - Do not join order_items unnecessarily because
      it may duplicate review scores.

    EXAMPLE:

    Question:
    What is the average review score for on-time deliveries?

    SQL:

    SELECT AVG(r.review_score) AS avg_review_score
    FROM orders o
    JOIN reviews r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
      AND julianday(o.order_delivered_customer_date)
          <= julianday(o.order_estimated_delivery_date);


    10. ORDERS WITHOUT REVIEWS

    Use NOT EXISTS or LEFT JOIN.

    Count orders that have no matching review records.


    11. MULTIPLE SELLERS

    Group order_items by order_id.

    Use:
    COUNT(DISTINCT seller_id) > 1


    12. SELLER AND CUSTOMER STATES

    To compare seller and customer states, join:

    order_items -> orders -> customers

    and

    order_items -> sellers

    Compare:
    sellers.seller_state = customers.customer_state

    For percentage of items from the same state:

    Count matching item rows divided by all relevant
    item rows, multiplied by 100.0.

    Do not use COUNT(DISTINCT order_id) when the
    question specifically asks for percentage of items.


    13. FREIGHT PERCENTAGE

    Calculate:

    100.0 * SUM(freight_value)
    / NULLIF(SUM(price), 0)


    14. CREDIT CARD INSTALLMENTS

    Use:
    AVG(payment_installments)

    Filter:
    payment_type = 'credit_card'


    15. PERCENTAGES

    Multiply ratios by 100.0.

    Use NULLIF to prevent division by zero.


    16. DATE FILTERING

    For a specific year, use the correct date column.

    For purchase year:
    strftime('%Y', order_purchase_timestamp)

    For purchase month:
    strftime('%Y-%m', order_purchase_timestamp)

    Never invent data for years not available.

    For month-over-month growth:
    Use LAG() to get the previous month's value.

    Growth percentage:
    100.0 * (current_value - previous_value)
    / NULLIF(previous_value, 0)


    17. MISSING DATA

    If required data or columns are unavailable,
    return CANNOT_ANSWER.

    Examples:

    Profit margin requires cost data.

    Customer age requires age or birth-date data.

    Customer gender requires gender data.

    Churn prediction requires a predictive model.


    18. SQL SAFETY

    Generate exactly one read-only SELECT statement.

    Common table expressions using WITH are allowed
    when they produce a read-only SELECT query.

    Never generate:

    INSERT, UPDATE, DELETE, DROP, ALTER,
    CREATE, REPLACE, ATTACH, DETACH, PRAGMA.

    Never generate multiple SQL statements.


    19. RESULT LIMIT

    For queries returning individual records,
    use LIMIT 100 or less.

    For top-N questions, use the requested LIMIT.

    Do not add unnecessary LIMIT to a single-row
    aggregate query.


    20. ACCURACY

    Use only existing tables and columns from metadata.

    Use correct JOIN conditions.

    Avoid unnecessary JOINs.

    Avoid duplicate counting from one-to-many relationships.

    Do not confuse payment value with item revenue.

    Do not invent columns, tables, or values.

    Do not automatically apply delivered-order filters
    to item revenue questions.

    If the question cannot be answered using
    the database, return exactly:

    CANNOT_ANSWER


    OUTPUT RULES:

    Return only SQLite SELECT SQL or CANNOT_ANSWER.

    No explanations.
    No markdown.
    No invented values.
    """

    # Step 3: Prepare the prompt
    prompt = f"""
    DATABASE METADATA:
    {metadata}

    USER QUESTION:
    {question}

    Generate the most accurate SQLite SELECT query.

    Check carefully:

    1. Are the necessary tables available?
    2. Are all required columns available?
    3. Are the JOIN conditions correct?
    4. Could any JOIN duplicate amounts or counts?
    5. Are the business rules correct?
    6. Is the requested year or month handled correctly?
    7. Is an order status filter actually required?
    8. Can the question actually be answered?

    Return SQL only.
    """

    # Step 4: Generate SQL using Groq
    sql = ask_llm(
        prompt=prompt,
        system_prompt=system_prompt
    )

    # Step 5: Clean generated SQL
    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```SQL", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

    return sql


# Step 6: Test advanced SQL generation
if __name__ == "__main__":

    questions = [
        "Which 3 sellers generated the highest item revenue? Show seller IDs and states.",
        "Which 3 sellers generated the highest item revenue from delivered orders? Show seller IDs and states."
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("QUESTION:", question)

        try:
            sql = generate_sql(question)

            print("\nGENERATED SQL:")
            print(sql)

        except Exception as error:
            print(
                "ERROR:",
                type(error).__name__,
                str(error)
            )