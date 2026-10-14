
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_jobs.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def find_column(df, keywords):
    """Find a column matching any supplied keyword."""
    for col in df.columns:
        name = col.lower().replace("_", " ")
        if any(word in name for word in keywords):
            return col
    return None


def main():
    print("\n===== JOBPULSE AI =====")
    print("Job Market Intelligence Platform")

    # Check dataset
    if not DATA_FILE.exists():
        print(f"Dataset not found: {DATA_FILE}")
        return

    # Load data
    df = pd.read_csv(DATA_FILE, low_memory=False)

    print(f"\nTotal job postings: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")

    # Missing-value report
    missing = df.isnull().sum().sort_values(ascending=False)
    missing.to_csv(
        REPORT_DIR / "missing_values_report.csv",
        header=["missing_count"]
    )
    print("Missing-value report saved.")

    # Detect columns
    title_col = find_column(df, ["job title", "title", "role"])
    company_col = find_column(df, ["company name", "company"])
    city_col = find_column(
        df, ["primary city", "city", "location"]
    )

    # Top job titles
    if title_col:
        print("\n--- TOP 10 JOB TITLES ---")
        titles = (
            df[title_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )
        print(titles.to_string())
        titles.to_csv(
            REPORT_DIR / "top_job_titles.csv",
            header=["job_count"]
        )

    # Top companies
    if company_col:
        print("\n--- TOP 10 COMPANIES ---")
        companies = (
            df[company_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )
        print(companies.to_string())
        companies.to_csv(
            REPORT_DIR / "top_companies.csv",
            header=["job_count"]
        )

    # Top locations
    if city_col:
        print("\n--- TOP 10 LOCATIONS ---")
        cities = (
            df[city_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )
        print(cities.to_string())
        cities.to_csv(
            REPORT_DIR / "top_locations.csv",
            header=["job_count"]
        )

    # Salary analysis using existing numeric columns
    print("\n--- SALARY ANALYSIS ---")

    required_cols = ["salary_min_lpa", "salary_max_lpa"]

    if all(col in df.columns for col in required_cols):
        min_salary = pd.to_numeric(
            df["salary_min_lpa"], errors="coerce"
        )
        max_salary = pd.to_numeric(
            df["salary_max_lpa"], errors="coerce"
        )

        # Exclude missing, undisclosed, and invalid salary ranges
        valid = (
            min_salary.gt(0)
            & max_salary.gt(0)
            & min_salary.le(max_salary)
        )

        salary_data = pd.DataFrame({
            "minimum_lpa": min_salary[valid],
            "maximum_lpa": max_salary[valid],
        })

        if not salary_data.empty:
            salary_data["midpoint_lpa"] = (
                salary_data["minimum_lpa"]
                + salary_data["maximum_lpa"]
            ) / 2

            print(
                f"Disclosed salary records: "
                f"{len(salary_data):,}"
            )
            print(
                f"Average salary midpoint: "
                f"{salary_data['midpoint_lpa'].mean():.2f} LPA"
            )
            print(
                f"Median salary midpoint: "
                f"{salary_data['midpoint_lpa'].median():.2f} LPA"
            )
            print(
                f"Minimum salary: "
                f"{salary_data['minimum_lpa'].min():.2f} LPA"
            )
            print(
                f"Maximum salary: "
                f"{salary_data['maximum_lpa'].max():.2f} LPA"
            )

            salary_data.to_csv(
                REPORT_DIR / "salary_analysis.csv",
                index=False
            )

            salary_data["midpoint_lpa"].describe().to_csv(
                REPORT_DIR / "salary_summary.csv"
            )

            print("Salary reports saved.")
        else:
            print(
                "No valid disclosed salary ranges found."
            )
    else:
        print(
            "Salary minimum/maximum columns not found."
        )

    print("\nAnalysis complete!")
    print(f"Reports saved in: {REPORT_DIR}")


if __name__ == "__main__":
    main()
