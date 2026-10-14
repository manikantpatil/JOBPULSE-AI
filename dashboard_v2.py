
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="JOBPULSE AI",
    page_icon="📊",
    layout="wide"
)

# ---------- THEME ----------
st.markdown("""
<style>
.stApp {
    background: #08111f;
    color: #edf5ff;
}
[data-testid="stSidebar"] {
    background: #101c2d;
}
h1, h2, h3 {
    color: #42e8cf !important;
}
[data-testid="stMetric"] {
    background: #122238;
    border: 1px solid #24405a;
    padding: 18px;
    border-radius: 12px;
}
div[data-testid="stMetricValue"] {
    color: #42e8cf;
}
</style>
""", unsafe_allow_html=True)

st.title("JOBPULSE AI")
st.caption("AI-powered job market and skills intelligence dashboard")

# ---------- LOAD DATA ----------
DATA_PATH = Path("data/processed/cleaned_jobs.csv")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Place your cleaned_jobs.csv file inside "
        "data/processed/ in your project folder."
    )
    st.write("Files currently available in the project:")
    for file in Path(".").glob("*.csv"):
        st.write(str(file))
    st.stop()

df = load_data(str(DATA_PATH))

if df.empty:
    st.warning("Your CSV file contains no job records.")
    st.stop()

# ---------- DETECT COLUMNS ----------
def find_column(possible_names):
    lookup = {str(c).lower().strip(): c for c in df.columns}
    for name in possible_names:
        if name in lookup:
            return lookup[name]
    for c in df.columns:
        if any(name in str(c).lower() for name in possible_names):
            return c
    return None

title_col = find_column(["job_title", "title", "job title", "position"])
company_col = find_column(["company", "company_name", "employer"])
location_col = find_column(["location", "job_location", "city"])
skills_col = find_column(["skills", "required_skills", "skill"])
salary_col = find_column(["salary", "salary_range", "average_salary"])
experience_col = find_column(["experience", "experience_level"])
work_col = find_column(["work_mode", "work_type", "remote_type"])
employment_col = find_column(["employment_type", "job_type"])

# ---------- FILTERS ----------
filtered = df.copy()

st.sidebar.header("🔎 Job Filters")

def add_filter(column, label):
    global filtered
    if column is not None:
        values = sorted(
            filtered[column].dropna().astype(str).unique().tolist()
        )
        chosen = st.sidebar.multiselect(label, values)
        if chosen:
            filtered = filtered[filtered[column].astype(str).isin(chosen)]

add_filter(location_col, "Location")
add_filter(title_col, "Job Title")
add_filter(company_col, "Company")
add_filter(experience_col, "Experience")
add_filter(work_col, "Work Mode")
add_filter(employment_col, "Employment Type")

keyword = st.sidebar.text_input("Search jobs or skills")
if keyword:
    text_columns = [
        c for c in [title_col, company_col, skills_col, location_col]
        if c is not None
    ]
    if text_columns:
        mask = filtered[text_columns].astype(str).apply(
            lambda col: col.str.contains(keyword, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask]

# ---------- KPI CARDS ----------
st.subheader("📌 Market Snapshot")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Job Listings", f"{len(filtered):,}")
c2.metric(
    "Companies",
    filtered[company_col].nunique()
    if company_col else "N/A"
)
c3.metric(
    "Locations",
    filtered[location_col].nunique()
    if location_col else "N/A"
)
c4.metric(
    "Unique Job Titles",
    filtered[title_col].nunique()
    if title_col else "N/A"
)

st.divider()

overview, skills_tab, explorer = st.tabs([
    "📈 Market Overview",
    "🧠 Skills Intelligence",
    "💼 Job Explorer"
])

# ---------- OVERVIEW ----------
with overview:
    left, right = st.columns(2)

    with left:
        st.subheader("Most Common Job Titles")
        if title_col:
            counts = filtered[title_col].fillna("Unknown").value_counts().head(12)
            fig = px.bar(
                x=counts.values,
                y=counts.index,
                orientation="h",
                labels={"x": "Listings", "y": "Job Title"},
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#08111f",
                plot_bgcolor="#08111f",
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("A job-title column was not detected.")

    with right:
        st.subheader("Jobs by Location")
        if location_col:
            counts = filtered[location_col].fillna("Unknown").value_counts().head(12)
            fig = px.pie(
                values=counts.values,
                names=counts.index,
                hole=0.55,
                template="plotly_dark"
            )
            fig.update_layout(paper_bgcolor="#08111f")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("A location column was not detected.")

    if salary_col:
        st.subheader("Salary Distribution")
        salary_values = pd.to_numeric(
            filtered[salary_col].astype(str).str.replace(
                r"[^0-9.]", "", regex=True
            ),
            errors="coerce"
        ).dropna()
        if not salary_values.empty:
            fig = px.histogram(
                x=salary_values,
                nbins=25,
                labels={"x": "Salary", "y": "Listings"},
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#08111f",
                plot_bgcolor="#08111f"
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------- SKILLS ----------
with skills_tab:
    st.subheader("Skills Demand Analysis")
    st.caption("Counts how often each skill appears in the filtered job listings.")

    if skills_col:
        skill_list = [
            "Python", "SQL", "Power BI", "Data Science",
            "Machine Learning", "Artificial Intelligence",
            "Excel", "Tableau", "TensorFlow", "PyTorch",
            "Deep Learning", "AWS", "Azure", "NLP"
        ]

        skill_counts = []
        text = filtered[skills_col].fillna("").astype(str)

        for skill in skill_list:
            count = text.str.contains(
                skill, case=False, regex=False
            ).sum()
            skill_counts.append({"Skill": skill, "Job Listings": int(count)})

        skill_df = pd.DataFrame(skill_counts).sort_values(
            "Job Listings", ascending=False
        )

        fig = px.bar(
            skill_df,
            x="Skill",
            y="Job Listings",
            color="Job Listings",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="#08111f",
            plot_bgcolor="#08111f",
            xaxis_tickangle=-35,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(skill_df, use_container_width=True, hide_index=True)
    else:
        st.warning(
            "No skills column detected. Check your CSV column names."
        )
        st.write("Available columns:", list(filtered.columns))

# ---------- JOB EXPLORER ----------
with explorer:
    st.subheader("Explore Job Listings")
    st.write(f"Showing {len(filtered):,} matching listings.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Filtered Jobs (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="jobpulse_filtered_jobs.csv",
        mime="text/csv"
    )

st.caption("JOBPULSE AI • Insights depend on the quality and coverage of your dataset.")
