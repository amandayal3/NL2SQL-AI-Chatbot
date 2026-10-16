from pathlib import Path
import pandas as pd

# Find the processed data folder
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data" / "processed"

# Read datasets
orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
items = pd.read_csv(DATA_DIR / "order_items.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
sellers = pd.read_csv(DATA_DIR / "sellers.csv")
payments = pd.read_csv(DATA_DIR / "payments.csv")
reviews = pd.read_csv(DATA_DIR / "reviews.csv")


# Function to check relationships
def check_relationship(child, parent, column, name):

    # Find IDs that do not exist in the parent table
    missing = ~child[column].isin(parent[column])

    print(name, ":", missing.sum(), "unmatched rows")


print("\n----- DATASET RELATIONSHIP CHECK -----")

# Orders and Customers
check_relationship(
    orders, customers, "customer_id",
    "Orders -> Customers"
)

# Order Items and Orders
check_relationship(
    items, orders, "order_id",
    "Order Items -> Orders"
)

# Order Items and Products
check_relationship(
    items, products, "product_id",
    "Order Items -> Products"
)

# Order Items and Sellers
check_relationship(
    items, sellers, "seller_id",
    "Order Items -> Sellers"
)

# Payments and Orders
check_relationship(
    payments, orders, "order_id",
    "Payments -> Orders"
)

# Reviews and Orders
check_relationship(
    reviews, orders, "order_id",
    "Reviews -> Orders"
)