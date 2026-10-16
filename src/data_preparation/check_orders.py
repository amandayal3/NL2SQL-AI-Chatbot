from pathlib import Path
import pandas as pd


# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Location of the orders dataset
FILE_PATH = PROJECT_DIR / "data" / "raw" / "olist_orders_dataset.csv"


def check_orders():
    """Check order statuses, missing dates, and duplicate IDs."""

    orders = pd.read_csv(FILE_PATH)

    # Count orders by their status
    print("\n1. Order Status:")
    print(orders["order_status"].value_counts())

    # Check missing delivery dates for each status
    print("\n2. Missing Delivery Dates by Status:")
    print(
        orders.groupby("order_status")[
            "order_delivered_customer_date"
        ].apply(lambda column: column.isna().sum())
    )

    # Check duplicate order IDs
    print("\n3. Duplicate Order IDs:")
    print(orders["order_id"].duplicated().sum())

    # Check purchase date range
    print("\n4. Purchase Date Range:")
    purchase_dates = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    print("Earliest:", purchase_dates.min())
    print("Latest:", purchase_dates.max())


if __name__ == "__main__":
    check_orders()