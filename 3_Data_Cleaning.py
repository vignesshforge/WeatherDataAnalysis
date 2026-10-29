import streamlit as st
import pandas as pd

from utils.data_processing import load_dataset, save_dataset
from utils.style import apply_custom_style

st.set_page_config(
    page_title="Data Cleaning",
    page_icon="🧹",
    layout="wide"
)

apply_custom_style()


st.title("🧹 Weather Data Cleaning")

df = load_dataset()

if df is None or df.empty:
    st.warning("Please upload a dataset first.")

else:
    st.subheader("Original Dataset")
    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", len(df))
    col2.metric("Missing Values", int(df.isna().sum().sum()))
    col3.metric("Duplicate Rows", int(df.duplicated().sum()))

    missing_method = st.selectbox(
        "How should missing values be handled?",
        [
            "Keep unchanged",
            "Remove rows with missing values",
            "Fill numeric missing values with mean"
        ]
    )

    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True
    )

    if st.button("Clean Dataset"):

        cleaned_df = df.copy()

        if missing_method == "Remove rows with missing values":
            cleaned_df = cleaned_df.dropna()

        elif missing_method == "Fill numeric missing values with mean":

            numeric_columns = cleaned_df.select_dtypes(
                include="number"
            ).columns

            for column in numeric_columns:
                mean_value = cleaned_df[column].mean()

                if pd.notna(mean_value):
                    cleaned_df[column] = cleaned_df[column].fillna(
                        mean_value
                    )

        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()

        st.session_state["cleaned_weather_df"] = cleaned_df

        st.success("Cleaning completed!")

        st.subheader("Cleaned Dataset")
        st.dataframe(cleaned_df, use_container_width=True)

        col1, col2 = st.columns(2)

        col1.metric("Rows Before", len(df))
        col2.metric("Rows After", len(cleaned_df))

        st.download_button(
            "Download Cleaned Dataset",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_weather_data.csv",
            mime="text/csv"
        )

        if st.button("Set Cleaned Dataset as Active"):
            save_dataset(cleaned_df)
            st.success("Cleaned dataset is now active!")
