from pathlib import Path
import pandas as pd


# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Folder containing our original CSV files
DATA_DIR = PROJECT_DIR / "data" / "raw"


def explore_dataset():
    """Explore all CSV files in the raw data folder."""

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw.")
        return

    for file_path in csv_files:
        print("\n" + "=" * 50)
        print("File:", file_path.name)

        # Read the CSV file
        data = pd.read_csv(file_path)

        # Display basic information
        print("Rows:", data.shape[0])
        print("Columns:", data.shape[1])
        print("Column names:", data.columns.tolist())

        # Check missing values and duplicate rows
        print("\nMissing values:")
        print(data.isnull().sum())

        print("\nDuplicate rows:", data.duplicated().sum())

        # Display the first five records
        print("\nFirst 5 rows:")
        print(data.head())


if __name__ == "__main__":
    explore_dataset()