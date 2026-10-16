import sqlite3
import json
from pathlib import Path

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# File locations
DATABASE_PATH = PROJECT_DIR / "database" / "ecommerce.db"
METADATA_PATH = PROJECT_DIR / "metadata" / "schema_metadata.json"


def generate_metadata():
    """Read SQLite schema and save it as JSON."""

    # Connect to the database
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        # Get all table names
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        tables = cursor.fetchall()

        # Store metadata here
        metadata = {}

        for table in tables:
            table_name = table[0]

            # Get column information
            cursor.execute(
                f'PRAGMA table_info("{table_name}")'
            )

            columns = cursor.fetchall()

            column_details = []

            for column in columns:
                column_details.append({
                    "name": column[1],
                    "type": column[2],
                    "primary_key": bool(column[5])
                })

            metadata[table_name] = {
                "columns": column_details
            }

        # Save metadata to JSON
        METADATA_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(METADATA_PATH, "w") as file:
            json.dump(metadata, file, indent=4)

        print("\n----- SCHEMA METADATA -----")

        for table_name, details in metadata.items():
            print(
                f"{table_name}: "
                f"{len(details['columns'])} columns"
            )

        print("\nMetadata generated successfully!")
        print("Saved to:", METADATA_PATH)

    finally:
        connection.close()


if __name__ == "__main__":
    generate_metadata()