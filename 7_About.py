import streamlit as st
from utils.style import apply_custom_style

st.set_page_config(
    page_title="About",
    page_icon="ℹ️",
    layout="wide"
)

apply_custom_style()


st.title("ℹ️ About the Project")

st.header("Weather Data Analysis System")

st.write("""
The Weather Data Analysis System is a Python-based application
designed to explore, clean, analyze, and visualize weather datasets.
""")

st.subheader("Objectives")

st.markdown("""
- Analyze weather data efficiently.
- Identify missing and duplicate records.
- Calculate statistical summaries.
- Visualize weather variables using interactive charts.
- Generate downloadable reports.
""")

st.subheader("Technologies Used")

st.markdown("""
- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Matplotlib
- Seaborn
- Scikit-learn
""")

st.subheader("Project Workflow")

st.markdown("""
1. Upload a weather dataset.
2. Preview and inspect the data.
3. Clean missing values and duplicates.
4. Analyze numerical weather variables.
5. Generate visualizations.
6. Export reports.
""")

st.info("This project is intended for educational and analytical purposes.")
