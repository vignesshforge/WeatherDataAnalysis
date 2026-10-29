import streamlit as st
import pandas as pd

from utils.data_processing import load_dataset, get_numeric_columns
from utils.style import apply_custom_style

st.set_page_config(
    page_title="Weather Reports",
    page_icon="📄",
    layout="wide"
)

apply_custom_style()


st.title("📄 Weather Analysis Reports")

df = load_dataset()

if df is None or df.empty:
    st.warning("Please upload a dataset first.")

else:
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Missing Values", int(df.isna().sum().sum()))

    st.subheader("Data Quality Report")

    quality = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    st.dataframe(quality, use_container_width=True)

    st.subheader("Statistical Report")

    numeric_columns = get_numeric_columns(df)

    if numeric_columns:
        report = df[numeric_columns].describe().T
        st.dataframe(report, use_container_width=True)

        st.download_button(
            "Download Statistical Report",
            data=report.to_csv().encode("utf-8"),
            file_name="weather_statistical_report.csv",
            mime="text/csv"
        )

    st.download_button(
        "Download Active Dataset",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="weather_dataset_report.csv",
        mime="text/csv"
    )
