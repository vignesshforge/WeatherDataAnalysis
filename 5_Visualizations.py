
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from utils.data_processing import load_dataset, get_numeric_columns
from utils.style import apply_custom_style

st.set_page_config(
    page_title="Advanced Weather Analytics",
    page_icon="📈",
    layout="wide"
)

apply_custom_style()


st.title("📈 Advanced Weather Analytics")

df = load_dataset()

if df is None or df.empty:
    st.warning("Please upload a weather dataset first.")
    st.stop()

# Work with a copy so filtering does not modify the original dataset.
df = df.copy()

st.success(f"Dataset loaded: {len(df)} records")

# --------------------------------------------------
# 1. DATE FILTER
# --------------------------------------------------

date_columns = [
    col for col in df.columns
    if "date" in col.lower() or "time" in col.lower()
]

filtered_df = df.copy()

if date_columns:
    date_col = st.selectbox("Select date column", date_columns)

    parsed_dates = pd.to_datetime(
        filtered_df[date_col],
        errors="coerce"
    )

    if parsed_dates.notna().any():
        filtered_df["_analysis_date"] = parsed_dates

        min_date = parsed_dates.min().date()
        max_date = parsed_dates.max().date()

        date_range = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_date, end_date = date_range

            filtered_df = filtered_df[
                filtered_df["_analysis_date"].dt.date.between(
                    start_date, end_date
                )
            ]

# --------------------------------------------------
# 2. CITY FILTER
# --------------------------------------------------

city_columns = [
    col for col in filtered_df.columns
    if col.lower() in ["city", "location", "station", "place"]
]

if city_columns:
    city_col = st.selectbox("Select city/location column", city_columns)

    cities = sorted(
        filtered_df[city_col].dropna().astype(str).unique().tolist()
    )

    selected_cities = st.multiselect(
        "Choose locations",
        cities,
        default=cities
    )

    filtered_df = filtered_df[
        filtered_df[city_col].astype(str).isin(selected_cities)
    ]

st.metric("Records after filtering", len(filtered_df))

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

numeric_columns = get_numeric_columns(filtered_df)

if not numeric_columns:
    st.warning("No numeric columns are available.")
    st.stop()

# --------------------------------------------------
# 3. WEATHER TREND ANALYSIS
# --------------------------------------------------

st.divider()
st.header("🌡️ Weather Trend Analysis")

if "_analysis_date" in filtered_df.columns:
    trend_x = "_analysis_date"
else:
    trend_x = st.selectbox(
        "Choose X-axis for trend analysis",
        filtered_df.columns.tolist()
    )

trend_y = st.selectbox(
    "Select weather variable",
    numeric_columns
)

trend_df = filtered_df[[trend_x, trend_y]].copy()

if trend_x == "_analysis_date":
    trend_df = trend_df.dropna(subset=[trend_x])
    trend_df = trend_df.sort_values(trend_x)

fig = px.line(
    trend_df,
    x=trend_x,
    y=trend_y,
    markers=True,
    title=f"{trend_y} Trend"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# 4. CITY-WISE COMPARISON
# --------------------------------------------------

st.divider()
st.header("🏙️ City-wise Weather Comparison")

if city_columns:
    comparison_variable = st.selectbox(
        "Choose variable to compare",
        numeric_columns,
        key="comparison_variable"
    )

    city_summary = (
        filtered_df.groupby(city_col)[comparison_variable]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        city_summary,
        x=city_col,
        y=comparison_variable,
        color=city_col,
        title=f"Average {comparison_variable} by Location",
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info(
        "No city/location column was detected. "
        "City comparison requires a column such as City or Location."
    )

# --------------------------------------------------
# 5. RAINFALL ANALYSIS
# --------------------------------------------------

st.divider()
st.header("🌧️ Rainfall Analysis")

rainfall_columns = [
    col for col in numeric_columns
    if "rain" in col.lower() or "precip" in col.lower()
]

if rainfall_columns:
    rainfall_col = st.selectbox(
        "Select rainfall column",
        rainfall_columns
    )

    if "_analysis_date" in filtered_df.columns:
        rainfall_df = filtered_df.dropna(
            subset=["_analysis_date"]
        ).copy()

        rainfall_df = (
            rainfall_df.groupby("_analysis_date")[rainfall_col]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            rainfall_df,
            x="_analysis_date",
            y=rainfall_col,
            title="Rainfall Over Time"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif city_columns:
        rainfall_summary = (
            filtered_df.groupby(city_col)[rainfall_col]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            rainfall_summary,
            x=city_col,
            y=rainfall_col,
            title="Total Rainfall by Location"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(
            "Rainfall data is available, but a date or location "
            "column is needed for grouped rainfall analysis."
        )

else:
    st.info(
        "No rainfall column detected. Look for a column named "
        "Rainfall, Precipitation, or a similar term."
    )

# --------------------------------------------------
# 6. CORRELATION HEATMAP
# --------------------------------------------------

st.divider()
st.header("🔥 Weather Correlation Heatmap")

if len(numeric_columns) >= 2:
    correlation = filtered_df[numeric_columns].corr()

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.heatmap(
        correlation,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        ax=ax
    )

    ax.set_title("Correlation Between Numeric Variables")

    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Correlation measures the strength of linear relationships. "
        "It does not prove that one variable causes another."
    )

else:
    st.info("At least two numeric columns are required for correlation analysis.")

# --------------------------------------------------
# 7. DOWNLOAD FILTERED DATA
# --------------------------------------------------

st.divider()
st.header("📥 Export Filtered Data")

download_df = filtered_df.drop(
    columns=["_analysis_date"],
    errors="ignore"
)

st.download_button(
    "Download Filtered Dataset",
    data=download_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_weather_data.csv",
    mime="text/csv"
)

