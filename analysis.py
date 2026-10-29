
import pandas as pd
import numpy as np


# --------------------------------------------------
# 1. Normalize column names
# --------------------------------------------------

def normalize_columns(df):
    """Remove unnecessary spaces from column names."""
    result = df.copy()
    result.columns = [
        str(column).strip() for column in result.columns
    ]
    return result


# --------------------------------------------------
# 2. Detect date column
# --------------------------------------------------

def detect_date_column(df):
    """Find a recognizable date or timestamp column."""
    date_names = [
        "date",
        "datetime",
        "timestamp",
        "time"
    ]

    for column in df.columns:
        if str(column).strip().lower() in date_names:
            return column

    return None


# --------------------------------------------------
# 3. Identify numeric columns
# --------------------------------------------------

def get_numeric_columns(df):
    """Return columns containing numeric data."""
    return df.select_dtypes(
        include=np.number
    ).columns.tolist()


# --------------------------------------------------
# 4. Identify weather measurement columns
# --------------------------------------------------

def get_weather_columns(df):
    """Identify common weather-related columns."""
    result = {}

    keywords = {
        "temperature": ["temperature", "temp"],
        "humidity": ["humidity"],
        "rainfall": ["rainfall", "rain", "precipitation"],
        "wind_speed": ["wind_speed", "windspeed", "wind speed"],
        "pressure": ["pressure"],
        "uv_index": ["uv_index", "uv index"]
    }

    for category, terms in keywords.items():
        for column in df.columns:
            column_name = str(column).strip().lower()

            if any(term in column_name for term in terms):
                if category not in result:
                    result[category] = column
                break

    return result


# --------------------------------------------------
# 5. Clean weather data
# --------------------------------------------------

def clean_weather_data(df, fill_missing=True, remove_duplicates=True):
    """
    Clean a weather dataset by:
    - Normalizing column names
    - Converting recognized date columns
    - Replacing infinite numeric values
    - Optionally removing duplicate rows
    - Optionally filling numeric missing values with medians
    """
    result = normalize_columns(df)

    date_column = detect_date_column(result)

    if date_column is not None:
        result[date_column] = pd.to_datetime(
            result[date_column],
            errors="coerce"
        )

    numeric_columns = get_numeric_columns(result)

    if numeric_columns:
        result[numeric_columns] = result[numeric_columns].replace(
            [np.inf, -np.inf],
            np.nan
        )

    if remove_duplicates:
        result = result.drop_duplicates()

    if fill_missing:
        numeric_columns = get_numeric_columns(result)

        for column in numeric_columns:
            median_value = result[column].median()

            if pd.notna(median_value):
                result[column] = result[column].fillna(
                    median_value
                )

    return result


# --------------------------------------------------
# 6. Generate descriptive statistics
# --------------------------------------------------

def get_summary_statistics(df):
    """Calculate descriptive statistics for numeric columns."""
    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        return pd.DataFrame()

    return df[numeric_columns].describe().T


# --------------------------------------------------
# 7. Filter by city
# --------------------------------------------------

def filter_by_city(df, city, city_column=None):
    """Return records matching the selected city."""
    if city_column is None:
        city_candidates = [
            column for column in df.columns
            if str(column).strip().lower()
            in ["city", "location", "place"]
        ]

        if not city_candidates:
            return df.copy()

        city_column = city_candidates[0]

    if city_column not in df.columns:
        return df.copy()

    return df[
        df[city_column].astype(str).str.casefold()
        == str(city).strip().casefold()
    ].copy()


# --------------------------------------------------
# 8. Filter by date range
# --------------------------------------------------

def filter_by_date_range(
    df,
    start_date,
    end_date,
    date_column=None
):
    """Return records within an inclusive date range."""
    result = df.copy()

    if date_column is None:
        date_column = detect_date_column(result)

    if date_column is None or date_column not in result.columns:
        return result

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    valid_dates = result[date_column].notna()

    return result[
        valid_dates
        & (result[date_column] >= start_date)
        & (result[date_column] < end_date + pd.Timedelta(days=1))
    ].copy()


# --------------------------------------------------
# 9.

