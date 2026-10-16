import sqlite3
from pathlib import Path

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Database location
DATABASE_PATH = PROJECT_DIR / "database" / "ecommerce.db"


def verify_database():
    """Check database tables and run a sample SQL query."""

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        # Find all tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )

        tables = cursor.fetchall()

        print("\n----- DATABASE TABLES -----")

        # Count rows in each table
        for table in tables:
            table_name = table[0]

            cursor.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            )

            total_rows = cursor.fetchone()[0]

            print(f"{table_name}: {total_rows} rows")

        # Run a simple SQL query
        print("\n----- SAMPLE SQL QUERY -----")

        cursor.execute("""
            SELECT order_status, COUNT(*)
            FROM orders
            GROUP BY order_status
            ORDER BY COUNT(*) DESC
        """)

        results = cursor.fetchall()

        for status, count in results:
            print(f"{status}: {count}")

        print("\nDatabase verification completed!")

    finally:
        connection.close()


if __name__ == "__main__":
    verify_database()