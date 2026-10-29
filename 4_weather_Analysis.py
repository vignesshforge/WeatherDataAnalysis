import streamlit as st

from utils.data_processing import load_dataset, get_numeric_columns
from utils.style import apply_custom_style

st.set_page_config(
    page_title="Weather Analysis",
    page_icon="🌦️",
    layout="wide"
)

apply_custom_style()


st.title("🌦️ Weather Data Analysis")

df = load_dataset()

if df is None or df.empty:
    st.warning("Please upload a weather dataset first.")

else:
    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.warning("No numeric columns are available for analysis.")

    else:
        st.subheader("Select a Weather Variable")

        column = st.selectbox(
            "Choose a numeric column",
            numeric_columns
        )

        values = df[column].dropna()

        if values.empty:
            st.warning("This column contains no valid numeric values.")

        else:
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Average", f"{values.mean():.2f}")
            col2.metric("Maximum", f"{values.max():.2f}")
            col3.metric("Minimum", f"{values.min():.2f}")
            col4.metric("Standard Deviation", f"{values.std():.2f}")

            st.subheader(f"Analysis of {column}")

            st.write(
                values.describe().to_frame("Statistics")
            )

            st.subheader("Frequency Distribution")

            histogram = __import__("plotly.express", fromlist=["express"])

            fig = histogram.histogram(
                df,
                x=column,
                title=f"Distribution of {column}"
            )

            st.plotly_chart(fig, use_container_width=True)
