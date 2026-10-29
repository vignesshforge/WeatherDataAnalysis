
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from utils.style import apply_custom_style

st.set_page_config(
    page_title="City & Date Filters",
    page_icon="🌦️",
    layout="wide"
)

apply_custom_style()


st.title("🌦️ City Search & Date-Range Filters")
st.write(
    "Select a city and date range to analyze your weather dataset."
)

# --------------------------------------------------
# 1. Load the dataset
# --------------------------------------------------

@st.cache_data
def load_csv(file_path, modified_time):
    return pd.read_csv(file_path)


uploaded_file = st.file_uploader(
    "Upload your weather CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the uploaded file: {error}")
        st.stop()
else:
    possible_files = [
        Path("data/weather_data.csv"),
        Path("data/sample_weather.csv")
    ]

    dataset_path = next(
        (path for path in possible_files if path.exists()),
        None
    )

    if dataset_path is None:
        st.warning(
            "No default dataset found. Upload a weather CSV file to continue."
        )
        st.stop()

    try:
        df = load_csv(
            str(dataset_path),
            dataset_path.stat().st_mtime
        )
    except Exception as error:
        st.error(f"Could not load the dataset: {error}")
        st.stop()


if df.empty:
    st.warning("The dataset is empty.")
    st.stop()


# --------------------------------------------------
# 2. Identify date and city columns
# --------------------------------------------------

st.subheader("📋 Dataset Information")

st.write("Available columns:", ", ".join(map(str, df.columns)))

date_candidates = [
    column for column in df.columns
    if str(column).strip().lower() in
    ["date", "datetime", "timestamp", "time"]
]

city_candidates = [
    column for column in df.columns
    if str(column).strip().lower() in
    ["city", "location", "place"]
]

if not date_candidates:
    st.error(
        "A date column is required. Name it Date, Datetime, Timestamp, or Time."
    )
    st.stop()

date_column = date_candidates[0]

df[date_column] = pd.to_datetime(
    df[date_column],
    errors="coerce"
)

df = df.dropna(subset=[date_column]).copy()

if df.empty:
    st.error("No valid dates were found in the dataset.")
    st.stop()


# --------------------------------------------------
# 3. City and date filters
# --------------------------------------------------

st.subheader("🔎 Filter Weather Records")

filter_col1, filter_col2 = st.columns(2)

if city_candidates:
    city_column = city_candidates[0]

    with filter_col1:
        cities = sorted(
            df[city_column].dropna().astype(str).unique().tolist()
        )

        selected_cities = st.multiselect(
            "Select city or cities",
            options=cities,
            default=cities
        )

    filtered_df = df[
        df[city_column].astype(str).isin(selected_cities)
    ].copy()

else:
    filtered_df = df.copy()
    st.info(
        "No City or Location column was found. "
        "Date filtering will still be available."
    )

min_date = df[date_column].min().date()
max_date = df[date_column].max().date()

with filter_col2:
    selected_dates = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

if not selected_cities if city_candidates else False:
    st.warning("Select at least one city.")
    st.stop()

if not isinstance(selected_dates, (tuple, list)):
    st.info("Select both a start date and an end date.")
    st.stop()

if len(selected_dates) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    st.error("The start date must be before the end date.")
    st.stop()

filtered_df = filtered_df[
    (filtered_df[date_column].dt.date >= start_date) &
    (filtered_df[date_column].dt.date <= end_date)
].copy()


# --------------------------------------------------
# 4. Display filtered results
# --------------------------------------------------

st.divider()
st.subheader("📊 Filtered Weather Summary")

if filtered_df.empty:
    st.warning(
        "No records match the selected city and date range. "
        "Try changing your filters."
    )
    st.stop()

metric_columns = st.columns(3)

metric_columns[0].metric(
    "Total Records",
    f"{len(filtered_df):,}"
)

metric_columns[1].metric(
    "Start Date",
    start_date.strftime("%d %b %Y")
)

metric_columns[2].metric(
    "End Date",
    end_date.strftime("%d %b %Y")
)

# Identify common weather measurements
numeric_columns = filtered_df.select_dtypes(
    include="number"
).columns.tolist()

temperature_candidates = [
    column for column in numeric_columns
    if "temperature" in str(column).lower()
    or str(column).strip().lower() in ["temp", "temp_c", "temp_f"]
]

rainfall_candidates = [
    column for column in numeric_columns
    if "rain" in str(column).lower()
    or "precipitation" in str(column).lower()
]

humidity_candidates = [
    column for column in numeric_columns
    if "humidity" in str(column).lower()
]

summary_columns = st.columns(3)

if temperature_candidates:
    temperature_column = temperature_candidates[0]
    summary_columns[0].metric(
        "Average Temperature",
        f"{filtered_df[temperature_column].mean():.1f}"
    )

if humidity_candidates:
    humidity_column = humidity_candidates[0]
    summary_columns[1].metric(
        "Average Humidity",
        f"{filtered_df[humidity_column].mean():.1f}%"
    )

if rainfall_candidates:
    rainfall_column = rainfall_candidates[0]
    summary_columns[2].metric(
        "Total Rainfall",
        f"{filtered_df[rainfall_column].sum():.1f}"
    )


# --------------------------------------------------
# 5. Temperature trend chart
# --------------------------------------------------

if temperature_candidates:
    st.subheader("🌡️ Temperature Trend")

    chart_df = filtered_df.sort_values(date_column)

    if city_candidates:
        fig = px.line(
            chart_df,
            x=date_column,
            y=temperature_column,
            color=city_column,
            markers=True,
            title="Temperature Over Time"
        )
    else:
        fig = px.line(
            chart_df,
            x=date_column,
            y=temperature_column,
            markers=True,
            title="Temperature Over Time"
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Temperature",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(
        "A numeric Temperature column was not found, "
        "so the temperature chart cannot be displayed."
    )


# --------------------------------------------------
# 6. Filtered dataset table
# --------------------------------------------------

st.subheader("📄 Filtered Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 7. Download filtered CSV
# --------------------------------------------------

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="filtered_weather_data.csv",
    mime="text/csv"
)

st.success("City and date filtering is ready!")

st.caption(
    "Note: The summary statistics are calculated only from the "
    "records matching your selected filters."
)

