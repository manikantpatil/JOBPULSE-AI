
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="JOBPULSE AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 JOBPULSE AI")
st.subheader("Job Market Intelligence Platform")
st.write("Explore job postings, companies, locations and salary trends.")

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data" / "processed" / "cleaned_jobs.csv"
)

if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}")
    st.info("Check that data/processed/cleaned_jobs.csv exists.")
    st.stop()

df = pd.read_csv(DATA_FILE, low_memory=False)

st.success("Job dataset loaded successfully!")

# Summary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Job Postings", f"{len(df):,}")

with col2:
    st.metric("Total Columns", len(df.columns))

with col3:
    company_col = next(
        (c for c in df.columns if "company" in c.lower()),
        None
    )
    total_companies = (
        df[company_col].nunique()
        if company_col else 0
    )
    st.metric("Unique Companies", total_companies)

st.divider()

# Job title analysis
title_col = next(
    (c for c in df.columns
     if "job title" in c.lower() or c.lower() == "title"),
    None
)

if title_col:
    st.subheader("Top 10 Job Titles")
    top_titles = df[title_col].dropna().value_counts().head(10)
    chart_data = top_titles.rename_axis("Job Title").reset_index(
        name="Job Count"
    )
    fig = px.bar(
        chart_data,
        x="Job Count",
        y="Job Title",
        orientation="h",
        title="Most Common Job Titles"
    )
    st.plotly_chart(fig, use_container_width=True)

# Salary analysis
st.subheader("Salary Analysis")

min_col = "salary_min_lpa"
max_col = "salary_max_lpa"

if min_col in df.columns and max_col in df.columns:
    salary = df[[min_col, max_col]].copy()

    for col in [min_col, max_col]:
        salary[col] = pd.to_numeric(salary[col], errors="coerce")

    salary = salary.dropna()
    salary = salary[
        (salary[min_col] > 0)
        & (salary[max_col] >= salary[min_col])
    ]

    if not salary.empty:
        salary["Midpoint LPA"] = (
            salary[min_col] + salary[max_col]
        ) / 2

        a, b = st.columns(2)
        a.metric(
            "Average Salary (LPA)",
            f"{salary['Midpoint LPA'].mean():.2f}"
        )
        b.metric(
            "Median Salary (LPA)",
            f"{salary['Midpoint LPA'].median():.2f}"
        )

        st.plotly_chart(
            px.histogram(
                salary,
                x="Midpoint LPA",
                nbins=30,
                title="Salary Distribution (LPA)"
            ),
            use_container_width=True
        )

        st.download_button(
            "Download Salary Analysis CSV",
            data=salary.to_csv(index=False),
            file_name="salary_analysis.csv",
            mime="text/csv"
        )
    else:
        st.warning("No valid disclosed salary values were found.")
else:
    st.info("Salary minimum/maximum columns are unavailable.")

# Dataset preview
st.subheader("Dataset Preview")
st.dataframe(df.head(100), use_container_width=True)

st.caption("JOBPULSE AI | Job Market Intelligence Dashboard")
