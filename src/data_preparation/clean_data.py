from pathlib import Path
import pandas as pd


# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Dataset folders
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


# --------------------------------------------------
# 1. CLEAN ORDERS DATASET
# --------------------------------------------------

def clean_orders():
    """Clean order dates and save the orders dataset."""

    input_file = RAW_DIR / "olist_orders_dataset.csv"
    output_file = PROCESSED_DIR / "orders.csv"

    # Read original orders dataset
    orders = pd.read_csv(input_file)

    # List of date columns
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    # Convert date columns into datetime format
    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    # Check duplicate order IDs
    duplicate_ids = orders["order_id"].duplicated().sum()

    # Check invalid delivery dates
    invalid_delivery = (
        orders["order_delivered_customer_date"]
        < orders["order_purchase_timestamp"]
    ).sum()

    # Save cleaned orders dataset
    orders.to_csv(output_file, index=False)

    print("\n----- ORDERS DATASET -----")
    print("Duplicate order IDs:", duplicate_ids)
    print("Invalid delivery dates:", invalid_delivery)
    print("Total rows:", len(orders))
    print("Orders cleaned successfully!")
    print("Saved to:", output_file)


# --------------------------------------------------
# 2. CLEAN CUSTOMERS DATASET
# --------------------------------------------------

def clean_customers():
    """Clean customer information and save the dataset."""

    input_file = RAW_DIR / "olist_customers_dataset.csv"
    output_file = PROCESSED_DIR / "customers.csv"

    # Read original customers dataset
    customers = pd.read_csv(input_file)

    # Check duplicate customer IDs
    duplicate_ids = customers["customer_id"].duplicated().sum()

    # Convert ZIP code prefixes into five-digit text
    customers["customer_zip_code_prefix"] = (
        customers["customer_zip_code_prefix"]
        .astype(str)
        .str.zfill(5)
    )

    # Remove extra spaces from city names
    customers["customer_city"] = (
        customers["customer_city"].str.strip()
    )

    # Save cleaned customers dataset
    customers.to_csv(output_file, index=False)

    print("\n----- CUSTOMERS DATASET -----")
    print("Duplicate customer IDs:", duplicate_ids)
    print("Total rows:", len(customers))
    print("Customers cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 3. CLEAN ORDER ITEMS DATASET
# --------------------------------------------------

def clean_order_items():
    """Check order item data and save a cleaned copy."""

    input_file = RAW_DIR / "olist_order_items_dataset.csv"
    output_file = PROCESSED_DIR / "order_items.csv"

    # Read original data
    order_items = pd.read_csv(input_file)

    # Check duplicate rows
    duplicate_rows = order_items.duplicated().sum()

    # Check invalid prices
    negative_prices = (order_items["price"] < 0).sum()

    # Check invalid shipping costs
    negative_freight = (order_items["freight_value"] < 0).sum()

    # Convert shipping deadline to datetime
    order_items["shipping_limit_date"] = pd.to_datetime(
        order_items["shipping_limit_date"],
        errors="coerce"
    )

    # Check whether any dates could not be converted
    invalid_dates = order_items["shipping_limit_date"].isna().sum()

    # Save cleaned dataset
    order_items.to_csv(output_file, index=False)

    print("\n----- ORDER ITEMS DATASET -----")
    print("Duplicate rows:", duplicate_rows)
    print("Negative prices:", negative_prices)
    print("Negative freight values:", negative_freight)
    print("Missing or invalid shipping dates:", invalid_dates)
    print("Total rows:", len(order_items))
    print("Order items cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 4. CLEAN PRODUCTS DATASET
# --------------------------------------------------

def clean_products():
    """Check product information and save a cleaned copy."""

    input_file = RAW_DIR / "olist_products_dataset.csv"
    output_file = PROCESSED_DIR / "products.csv"

    # Read original products dataset
    products = pd.read_csv(input_file)

    # Check duplicate product IDs
    duplicate_ids = products["product_id"].duplicated().sum()

    # Check missing product categories
    missing_categories = products["product_category_name"].isna().sum()

    # Columns containing product measurements
    measurement_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    # Check negative product measurements
    negative_measurements = (
        products[measurement_columns] < 0
    ).sum().sum()

    # Save cleaned products dataset
    products.to_csv(output_file, index=False)

    print("\n----- PRODUCTS DATASET -----")
    print("Duplicate product IDs:", duplicate_ids)
    print("Missing product categories:", missing_categories)
    print("Negative measurements:", negative_measurements)
    print("Total rows:", len(products))
    print("Products cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 5. CLEAN SELLERS DATASET
# --------------------------------------------------

def clean_sellers():
    """Clean seller information and save the dataset."""

    input_file = RAW_DIR / "olist_sellers_dataset.csv"
    output_file = PROCESSED_DIR / "sellers.csv"

    # Read original sellers dataset
    sellers = pd.read_csv(input_file)

    # Check duplicate seller IDs
    duplicate_ids = sellers["seller_id"].duplicated().sum()

    # Check missing values
    missing_values = sellers.isna().sum().sum()

    # Convert ZIP code prefixes into five-digit text
    sellers["seller_zip_code_prefix"] = (
        sellers["seller_zip_code_prefix"]
        .astype(str)
        .str.zfill(5)
    )

    # Remove extra spaces from city names
    sellers["seller_city"] = sellers["seller_city"].str.strip()

    # Save cleaned dataset
    sellers.to_csv(output_file, index=False)

    print("\n----- SELLERS DATASET -----")
    print("Duplicate seller IDs:", duplicate_ids)
    print("Missing values:", missing_values)
    print("Total rows:", len(sellers))
    print("Sellers cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 6. CLEAN PAYMENTS DATASET
# --------------------------------------------------

def clean_payments():
    """Check payment information and save a cleaned copy."""

    input_file = RAW_DIR / "olist_order_payments_dataset.csv"
    output_file = PROCESSED_DIR / "payments.csv"

    # Read original payments dataset
    payments = pd.read_csv(input_file)

    # Check duplicate rows
    duplicate_rows = payments.duplicated().sum()

    # Check missing values
    missing_values = payments.isna().sum().sum()

    # Check negative payment amounts
    negative_payments = (payments["payment_value"] < 0).sum()

    # Check negative installment counts
    negative_installments = (
        payments["payment_installments"] < 0
    ).sum()

    # Check available payment methods
    payment_methods = payments["payment_type"].value_counts()

    # Save cleaned dataset
    payments.to_csv(output_file, index=False)

    print("\n----- PAYMENTS DATASET -----")
    print("Duplicate rows:", duplicate_rows)
    print("Missing values:", missing_values)
    print("Negative payments:", negative_payments)
    print("Negative installments:", negative_installments)
    print("Total rows:", len(payments))

    print("\nPayment methods:")
    print(payment_methods)

    print("\nPayments cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 7. CLEAN REVIEWS DATASET
# --------------------------------------------------

def clean_reviews():
    """Check customer reviews and save a cleaned copy."""

    input_file = RAW_DIR / "olist_order_reviews_dataset.csv"
    output_file = PROCESSED_DIR / "reviews.csv"

    # Read original reviews dataset
    reviews = pd.read_csv(input_file)

    # Check duplicate rows
    duplicate_rows = reviews.duplicated().sum()

    # Check missing review titles
    missing_titles = reviews["review_comment_title"].isna().sum()

    # Check missing review messages
    missing_messages = reviews["review_comment_message"].isna().sum()

    # Check invalid ratings
    invalid_ratings = (
        (reviews["review_score"] < 1) |
        (reviews["review_score"] > 5)
    ).sum()

    # Convert review dates into datetime format
    date_columns = [
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in date_columns:
        reviews[column] = pd.to_datetime(
            reviews[column],
            errors="coerce"
        )

    # Calculate average rating
    average_rating = reviews["review_score"].mean()

    # Count reviews by rating
    rating_counts = reviews["review_score"].value_counts().sort_index()

    # Save cleaned dataset
    reviews.to_csv(output_file, index=False)

    print("\n----- REVIEWS DATASET -----")
    print("Duplicate rows:", duplicate_rows)
    print("Missing review titles:", missing_titles)
    print("Missing review messages:", missing_messages)
    print("Invalid ratings:", invalid_ratings)
    print("Average rating:", round(average_rating, 2))
    print("Total rows:", len(reviews))

    print("\nReviews by rating:")
    print(rating_counts)

    print("\nReviews cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 8. CLEAN GEOLOCATION DATASET
# --------------------------------------------------

def clean_geolocation():
    """Check geolocation data and save a cleaned copy."""

    input_file = RAW_DIR / "olist_geolocation_dataset.csv"
    output_file = PROCESSED_DIR / "geolocation.csv"

    # Read original geolocation dataset
    geolocation = pd.read_csv(input_file)

    # Check duplicate rows
    duplicate_rows = geolocation.duplicated().sum()

    # Check missing values
    missing_values = geolocation.isna().sum().sum()

    # Check invalid latitude
    invalid_latitude = (
        (geolocation["geolocation_lat"] < -90) |
        (geolocation["geolocation_lat"] > 90)
    ).sum()

    # Check invalid longitude
    invalid_longitude = (
        (geolocation["geolocation_lng"] < -180) |
        (geolocation["geolocation_lng"] > 180)
    ).sum()

    # Convert ZIP code prefixes into five-digit text
    geolocation["geolocation_zip_code_prefix"] = (
        geolocation["geolocation_zip_code_prefix"]
        .astype(str)
        .str.zfill(5)
    )

    # Remove extra spaces from city names
    geolocation["geolocation_city"] = (
        geolocation["geolocation_city"].str.strip()
    )

    # Save the dataset
    geolocation.to_csv(output_file, index=False)

    print("\n----- GEOLOCATION DATASET -----")
    print("Duplicate rows:", duplicate_rows)
    print("Missing values:", missing_values)
    print("Invalid latitude:", invalid_latitude)
    print("Invalid longitude:", invalid_longitude)
    print("Total rows:", len(geolocation))

    print("\nGeolocation cleaned successfully!")
    print("Saved to:", output_file)

# --------------------------------------------------
# 9. CLEAN CATEGORY TRANSLATION DATASET
# --------------------------------------------------

def clean_category_translation():
    """Check category translations and save the dataset."""

    input_file = RAW_DIR / "product_category_name_translation.csv"
    output_file = PROCESSED_DIR / "category_translation.csv"

    # Read original dataset
    categories = pd.read_csv(input_file)

    # Check duplicate rows
    duplicate_rows = categories.duplicated().sum()

    # Check duplicate Portuguese category names
    duplicate_categories = (
        categories["product_category_name"].duplicated().sum()
    )

    # Check missing values
    missing_values = categories.isna().sum().sum()

    # Remove extra spaces from category names
    categories["product_category_name"] = (
        categories["product_category_name"].str.strip()
    )

    categories["product_category_name_english"] = (
        categories["product_category_name_english"].str.strip()
    )

    # Save cleaned dataset
    categories.to_csv(output_file, index=False)

    print("\n----- CATEGORY TRANSLATION DATASET -----")
    print("Duplicate rows:", duplicate_rows)
    print("Duplicate category names:", duplicate_categories)
    print("Missing values:", missing_values)
    print("Total rows:", len(categories))

    print("\nCategory translation cleaned successfully!")
    print("Saved to:", output_file)
# --------------------------------------------------
# 3. RUN CLEANING FUNCTIONS
# --------------------------------------------------

if __name__ == "__main__":

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    clean_orders()
    clean_customers()
    clean_order_items()
    clean_products()
    clean_sellers()
    clean_payments()
    clean_reviews()
    clean_geolocation()
    clean_category_translation()

    print("\nAll nine datasets cleaned successfully!")