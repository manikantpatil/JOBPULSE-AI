
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "archive" / "job_postings.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_jobs.csv"


def main():
    print("===== JOBPULSE AI: DATA CLEANING =====")

    if not INPUT_FILE.exists():
        print(f"Dataset not found: {INPUT_FILE}")
        return

    # Load the dataset
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Original rows: {len(df)}")

    # Remove duplicate records
    df = df.drop_duplicates()

    # Clean column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Clean text columns
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Create output directory if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save cleaned dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned rows: {len(df)}")
    print(f"Duplicate and empty rows removed.")
    print(f"Saved cleaned dataset to:\n{OUTPUT_FILE}")
    print("\nCleaning completed successfully!")


if __name__ == "__main__":
    main()
