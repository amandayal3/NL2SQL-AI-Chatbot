import json
from config import METADATA_PATH


def retrieve_metadata(question):

    # Step 1: Load metadata
    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    question = question.lower()

    # Step 2: Define keywords for each table
    table_keywords = {
        "orders": [
            "order", "status", "purchase",
            "delivery", "deliveries", "delivered",
            "late", "on-time", "on time",
            "delayed", "arrival", "estimated"
        ],

        "customers": [
            "customer", "buyer", "city",
            "state", "location", "repeat"
        ],

        "order_items": [
            "item", "price", "revenue",
            "sales", "freight", "shipping cost"
        ],

        "products": [
            "product", "category", "weight",
            "height", "width", "length"
        ],

        "sellers": [
            "seller", "merchant", "vendor"
        ],

        "payments": [
            "payment", "installment", "credit card",
            "debit card", "voucher", "boleto"
        ],

        "reviews": [
            "review", "rating", "score",
            "feedback", "satisfaction"
        ],

        "category_translation": [
            "english category", "translated category",
            "translation", "english name"
        ],

        "geolocation": [
            "geolocation", "latitude", "longitude",
            "coordinates", "zip code"
        ]
    }

    # Step 3: Select tables using keywords
    selected_tables = set()

    for table_name, keywords in table_keywords.items():
        if any(word in question for word in keywords):
            selected_tables.add(table_name)

    # Step 4: Add required tables for JOINs

    # Reviews with delivery performance
    if "reviews" in selected_tables and any(
        word in question
        for word in [
            "delivery", "deliveries", "delivered",
            "late", "on-time", "on time",
            "early", "delayed"
        ]
    ):
        selected_tables.add("orders")

    # Product category review analysis
    if (
        "reviews" in selected_tables
        and "products" in selected_tables
    ):
        selected_tables.update([
            "orders",
            "order_items"
        ])

    # Seller revenue
    if "sellers" in selected_tables and any(
        word in question
        for word in ["revenue", "sales", "price", "sold"]
    ):
        selected_tables.add("order_items")

    # NEW: Seller order analysis and cancellation rates
    if (
        "sellers" in selected_tables
        and "orders" in selected_tables
    ):
        selected_tables.add("order_items")

    # Seller and customer state comparison
    if (
        "sellers" in selected_tables
        and "customers" in selected_tables
    ):
        selected_tables.update([
            "orders",
            "order_items"
        ])

    # Customer revenue
    if "customers" in selected_tables and any(
        word in question
        for word in ["revenue", "sales", "price", "spent"]
    ):
        selected_tables.update([
            "orders",
            "order_items"
        ])

    # Product revenue
    if "products" in selected_tables and any(
        word in question
        for word in ["revenue", "sales", "price", "sold"]
    ):
        selected_tables.add("order_items")

    # English product categories
    if "products" in selected_tables and any(
        word in question
        for word in ["english", "translated", "translation"]
    ):
        selected_tables.add("category_translation")

    # Payment analysis by month or year
    if "payments" in selected_tables and any(
        word in question
        for word in [
            "month", "year",
            "purchase date", "2017", "2018"
        ]
    ):
        selected_tables.add("orders")

    # Orders without reviews
    if (
        "orders" in selected_tables
        and "review" in question
    ):
        selected_tables.add("reviews")

    # Order items by order status
    if "order_items" in selected_tables and any(
        word in question
        for word in [
            "delivered", "canceled",
            "cancelled", "status"
        ]
    ):
        selected_tables.add("orders")

    # Products that have never been ordered
    if "products" in selected_tables and any(
        phrase in question
        for phrase in [
            "never been ordered",
            "never ordered",
            "not ordered",
            "without orders",
            "unsold products",
            "products with no orders",
            "never purchased",
            "not purchased"
        ]
    ):
        selected_tables.add("order_items")

    # Step 5: Find all available tables
    all_tables = {
        key
        for key, value in metadata.items()
        if key not in [
            "relationships",
            "business_rules"
        ]
        and isinstance(value, dict)
    }

    # Step 6: Fallback when no tables match
    if not selected_tables:
        selected_tables = all_tables

    # Step 7: Get selected table metadata
    relevant_metadata = {
        table_name: metadata[table_name]
        for table_name in metadata
        if table_name in selected_tables
    }

    # Step 8: Get relationships
    relevant_relationships = []

    for relationship in metadata.get("relationships", []):

        from_table = relationship.get("from_table")
        to_table = relationship.get("to_table")

        if (
            from_table in selected_tables
            and to_table in selected_tables
        ):
            relevant_relationships.append(relationship)

    # Step 9: Return metadata
    return {
        "tables": relevant_metadata,
        "relationships": relevant_relationships,
        "business_rules": metadata.get("business_rules", [])
    }