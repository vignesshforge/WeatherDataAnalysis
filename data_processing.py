from pathlib import Path
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "weather_data.csv"


def load_dataset():
    """Load the active weather dataset."""

    # First, check the current Streamlit session
    if "weather_df" in st.session_state:
        df = st.session_state["weather_df"]

        if isinstance(df, pd.DataFrame):
            return df.copy()

    # Otherwise, load the saved dataset
    if DATA_PATH.exists() and DATA_PATH.stat().st_size > 0:
        try:
            df = pd.read_csv(DATA_PATH)
            st.session_state["weather_df"] = df
            return df.copy()
        except Exception as error:
            st.error(f"Unable to load dataset: {error}")

    return None


def save_dataset(df):
    """Save a dataset as the active weather dataset."""

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(DATA_PATH, index=False)

    st.session_state["weather_df"] = df.copy()


def get_numeric_columns(df):
    """Return numeric columns from the dataset."""

    return df.select_dtypes(include="number").columns.tolist()