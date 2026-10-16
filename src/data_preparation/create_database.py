import sqlite3
from pathlib import Path
import pandas as pd

# Find main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Set folder paths
DATA_DIR = PROJECT_DIR / "data" / "processed"
DATABASE_PATH = PROJECT_DIR / "database" / "ecommerce.db"

# CSV filenames and database table names
tables = {
    "orders": "orders.csv",
    "customers": "customers.csv",
    "order_items": "order_items.csv",
    "products": "products.csv",
    "sellers": "sellers.csv",
    "payments": "payments.csv",
    "reviews": "reviews.csv",
    "geolocation": "geolocation.csv",
    "category_translation": "category_translation.csv"
}


def create_database():
    """Load processed CSV files into SQLite."""

    # Create database folder
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        # Load each CSV file
        for table_name, file_name in tables.items():

            file_path = DATA_DIR / file_name

            # Read CSV
            data = pd.read_csv(file_path)

            # Save as SQLite table
            data.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False
            )

            print(f"{table_name}: {len(data)} rows loaded")

        # Save changes
        connection.commit()

        print("\nDatabase created successfully!")
        print("Database location:", DATABASE_PATH)

    finally:
        # Close database connection
        connection.close()


if __name__ == "__main__":
    create_database()