import json
from pathlib import Path

# Find project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Metadata file
METADATA_PATH = PROJECT_DIR / "metadata" / "schema_metadata.json"


def add_metadata():
    """Add descriptions, relationships, and business rules."""

    # Read existing metadata
    with open(METADATA_PATH, "r") as file:
        metadata = json.load(file)

    # Table descriptions
    descriptions = {
        "customers": "Customer information including city and state.",
        "orders": "Order information including status and dates.",
        "order_items": "Products purchased in each order, including prices.",
        "products": "Product categories, weight, and dimensions.",
        "sellers": "Seller information including city and state.",
        "payments": "Payment methods, amounts, and installments.",
        "reviews": "Customer ratings and review comments.",
        "geolocation": "ZIP code locations with latitude and longitude.",
        "category_translation": "Portuguese to English product category names."
    }

    # Add descriptions to tables
    for table_name in metadata:
        metadata[table_name]["description"] = descriptions.get(
            table_name, ""
        )

    # Define relationships
    metadata["relationships"] = [
        {
            "from_table": "orders",
            "from_column": "customer_id",
            "to_table": "customers",
            "to_column": "customer_id"
        },
        {
            "from_table": "order_items",
            "from_column": "order_id",
            "to_table": "orders",
            "to_column": "order_id"
        },
        {
            "from_table": "order_items",
            "from_column": "product_id",
            "to_table": "products",
            "to_column": "product_id"
        },
        {
            "from_table": "order_items",
            "from_column": "seller_id",
            "to_table": "sellers",
            "to_column": "seller_id"
        },
        {
            "from_table": "payments",
            "from_column": "order_id",
            "to_table": "orders",
            "to_column": "order_id"
        },
        {
            "from_table": "reviews",
            "from_column": "order_id",
            "to_table": "orders",
            "to_column": "order_id"
        },
        {
            "from_table": "products",
            "from_column": "product_category_name",
            "to_table": "category_translation",
            "to_column": "product_category_name"
        }
    ]

    # Business rules for SQL generation
    metadata["business_rules"] = [
        "Use SQLite SQL syntax.",
        "Use only SELECT queries to read data.",
        "Use delivered orders when calculating completed sales.",
        "Calculate item sales using order_items.price.",
        "Do not include freight_value in item sales unless requested.",
        "Use COUNT(DISTINCT order_id) when counting unique orders.",
        "Use customers.customer_unique_id for unique customer counts.",
        "An order may have multiple items, payments, or reviews.",
        "Avoid double counting when joining multiple one-to-many tables.",
        "Use category_translation for English product category names.",
        "Geolocation may contain multiple rows per ZIP code. Do not join it directly for counting customers or sellers."
    ]

    # Save updated metadata
    with open(METADATA_PATH, "w") as file:
        json.dump(metadata, file, indent=4)

    print("Metadata descriptions added successfully!")
    print("Total relationships:", len(metadata["relationships"]))
    print("Total business rules:", len(metadata["business_rules"]))
    print("Updated file:", METADATA_PATH)


if __name__ == "__main__":
    add_metadata()