
import streamlit as st
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor

from utils.data_processing import load_dataset, get_numeric_columns
from utils.style import apply_custom_style


st.set_page_config(
    page_title="Weather Prediction",
    page_icon="🌤️",
    layout="wide"
)

apply_custom_style()


st.title("🌤️ Weather Temperature Prediction")

st.write(
    "Enter weather measurements to estimate temperature "
    "using a Random Forest machine-learning model."
)

st.info(
    "Educational demonstration only. Predictions depend on "
    "the quality and size of the uploaded dataset."
)

# Load dataset
df = load_dataset()

if df is None or df.empty:
    st.warning(
        "No dataset is available. Open Upload Dataset "
        "and load a weather CSV file first."
    )
    st.stop()

# Identify numeric columns
numeric_cols = get_numeric_columns(df)

if len(numeric_cols) < 2:
    st.error(
        "The dataset needs at least two numeric columns: "
        "one target column and one input feature."
    )
    st.stop()

# Find a likely temperature column
temperature_candidates = [
    col for col in numeric_cols
    if col.lower().strip() in [
        "temperature", "temp", "temperature_c"
    ]
]

default_target = (
    temperature_candidates[0]
    if temperature_candidates
    else numeric_cols[0]
)

st.subheader("⚙️ Configure the Prediction Model")

target_col = st.selectbox(
    "Select the value to predict",
    numeric_cols,
    index=numeric_cols.index(default_target)
)

feature_options = [
    col for col in numeric_cols
    if col != target_col
]

default_features = [
    col for col in feature_options
    if col.lower().strip() in [
        "humidity", "rainfall", "wind_speed", "windspeed"
    ]
]

if not default_features:
    default_features = feature_options[:min(3, len(feature_options))]

selected_features = st.multiselect(
    "Select input features",
    feature_options,
    default=default_features
)

if not selected_features:
    st.warning("Select at least one input feature.")
    st.stop()

# Prepare training data
model_df = df[selected_features + [target_col]].copy()

for col in selected_features + [target_col]:
    model_df[col] = pd.to_numeric(
        model_df[col],
        errors="coerce"
    )

model_df = model_df.replace(
    [np.inf, -np.inf],
    np.nan
).dropna()

st.write(f"Complete training records available: **{len(model_df)}**")

if len(model_df) < 10:
    st.error(
        "At least 10 complete records are required for this "
        "demonstration. A larger dataset is strongly recommended."
    )
    st.stop()

if model_df[target_col].nunique() < 2:
    st.error(
        "The selected target column must contain at least "
        "two different values."
    )
    st.stop()

# Train the model on all available complete records
X = model_df[selected_features]
y = model_df[target_col]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

st.success("Prediction model trained successfully!")

st.divider()

st.subheader("📝 Enter Weather Measurements")

st.write(
    "Enter values using the same units and approximate ranges "
    "as the training dataset."
)

input_values = {}

columns = st.columns(min(3, len(selected_features)))

for i, feature in enumerate(selected_features):
    with columns[i % len(columns)]:
        series = pd.to_numeric(
            df[feature],
            errors="coerce"
        ).replace([np.inf, -np.inf], np.nan).dropna()

        if series.empty:
            default_value = 0.0
            min_value = -1_000_000.0
            max_value = 1_000_000.0
        else:
            default_value = float(series.median())
            min_value = float(series.min())
            max_value = float(series.max())

            if min_value == max_value:
                min_value -= 1.0
                max_value += 1.0

        input_values[feature] = st.number_input(
            f"{feature}",
            min_value=min_value,
            max_value=max_value,
            value=float(np.clip(
                default_value,
                min_value,
                max_value
            )),
            key=f"prediction_input_{feature}"
        )

st.caption(
    "Input values are limited to the observed training-data "
    "range where possible. Predictions outside the data's "
    "typical conditions may be unreliable."
)

if st.button("🔮 Predict", type="primary"):
    input_df = pd.DataFrame(
        [input_values],
        columns=selected_features
    )

    prediction = float(model.predict(input_df)[0])

    st.subheader("🎯 Prediction Result")

    st.metric(
        label=f"Predicted {target_col}",
        value=f"{prediction:.2f}"
    )

    st.write("### Input Summary")
    st.dataframe(
        input_df,
        use_container_width=True,
        hide_index=True
    )

    result_df = input_df.copy()
    result_df[f"Predicted_{target_col}"] = prediction

    st.download_button(
        label="⬇️ Download Prediction",
        data=result_df.to_csv(index=False).encode("utf-8"),
        file_name="weather_prediction.csv",
        mime="text/csv"
    )

    st.success("Prediction completed!")

