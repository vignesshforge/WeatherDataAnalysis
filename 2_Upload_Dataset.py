
import streamlit as st
import pandas as pd
from pathlib import Path
from utils.style import apply_custom_style

apply_custom_style()

st.title("📂 Upload Weather Dataset")

st.write(
    "Choose a sample dataset, upload your Kaggle dataset, "
    "or upload another weather CSV file."
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

sample_path = DATA_DIR / "sample_weather.csv"
saved_path = DATA_DIR / "weather_data.csv"

source = st.radio(
    "Choose your dataset source",
    [
        "Use sample dataset",
        "Upload a CSV file",
        "Use previously saved dataset"
    ]
)

if source == "Use sample dataset":

    if sample_path.exists():
        try:
            df = pd.read_csv(sample_path)

            st.session_state["weather_df"] = df

            st.success("Sample dataset loaded successfully!")

            st.dataframe(df, use_container_width=True)

            st.metric("Total Records", len(df))
            st.metric("Total Columns", len(df.columns))

            if st.button("Save sample as active dataset"):
                df.to_csv(saved_path, index=False)
                st.success("Sample dataset saved successfully!")

        except Exception as e:
            st.error(f"Could not load sample dataset: {e}")

    else:
        st.error(
            "Sample dataset not found. Create "
            "data/sample_weather.csv first."
        )

elif source == "Upload a CSV file":

    uploaded_file = st.file_uploader(
        "Upload a weather CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df = pd.read_csv(uploaded_file)

            st.success("CSV file read successfully!")

            st.subheader("Dataset Preview")
            st.dataframe(df.head(20), use_container_width=True)

            col1, col2 = st.columns(2)

            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])

            st.write("Column names:")
            st.write(list(df.columns))

            if st.button("Save uploaded dataset as active dataset"):

                df.to_csv(saved_path, index=False)

                st.session_state["weather_df"] = df

                st.success(
                    "Dataset saved! Other pages can now use it."
                )

        except Exception as e:
            st.error(f"Unable to read the CSV file: {e}")

elif source == "Use previously saved dataset":

    if saved_path.exists() and saved_path.stat().st_size > 0:

        try:
            df = pd.read_csv(saved_path)

            st.session_state["weather_df"] = df

            st.success("Saved dataset loaded successfully!")

            st.dataframe(df.head(20), use_container_width=True)

        except Exception as e:
            st.error(f"Unable to load saved dataset: {e}")

    else:
        st.warning(
            "No saved dataset is available. "
            "Choose a sample or upload a CSV file first."
        )

