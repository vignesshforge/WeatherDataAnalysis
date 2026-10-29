import streamlit as st


def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5f7fb;
        }

        h1, h2, h3 {
            color: #1f3a5f;
        }

        [data-testid="stMetric"] {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )