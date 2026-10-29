
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from pathlib import Path
from utils.style import apply_custom_style


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Improved Weather Prediction",
    page_icon="🌦️",
    layout="wide"
)

apply_custom_style()


st.title("🌦️ Improved Weather Prediction")
st.write(
    "Train multiple machine-learning models, compare their performance, "
    "and predict weather measurements from historical data."
)

st.info(
    "This educational model estimates a selected weather variable from "
    "the available input features. It does not independently predict "
    "future weather conditions."
)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your weather CSV dataset",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read CSV: {error}")
        st.stop()
else:
    paths = [
        Path("data/weather_data.csv"),
        Path("data/sample_weather.csv")
    ]

    dataset_path = next(
        (path for path in paths if path.exists()),
        None
    )

    if dataset_path is None:
        st.warning("Upload a weather CSV file to begin.")
        st.stop()

    try:
        df = pd.read_csv(dataset_path)
    except Exception as error:
        st.error(f"Could not load dataset: {error}")
        st.stop()


if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

st.subheader("📋 Dataset Preview")
st.dataframe(df.head(10), use_container_width=True)

st.write(f"Rows: **{len(df)}** | Columns: **{len(df.columns)}**")


# --------------------------------------------------
# PREPARE FEATURES
# --------------------------------------------------

# Convert recognized date columns into useful numeric features.
data = df.copy()

date_columns = [
    column for column in data.columns
    if str(column).strip().lower()
    in ["date", "datetime", "timestamp"]
]

for column in date_columns:
    parsed_dates = pd.to_datetime(data[column], errors="coerce")

    data[f"{column}_year"] = parsed_dates.dt.year
    data[f"{column}_month"] = parsed_dates.dt.month
    data[f"{column}_day"] = parsed_dates.dt.day
    data[f"{column}_dayofyear"] = parsed_dates.dt.dayofyear

    data.drop(columns=[column], inplace=True)


# Convert numeric-looking text columns where possible.
for column in data.columns:
    if data[column].dtype == "object":
        converted = pd.to_numeric(data[column], errors="coerce")

        original_nonmissing = data[column].notna().sum()

        if (
            original_nonmissing > 0
            and converted.notna().sum() / original_nonmissing >= 0.8
        ):
            data[column] = converted


# Encode categorical variables using one-hot encoding.
data = pd.get_dummies(
    data,
    drop_first=False,
    dtype=int
)

# Remove infinite values.
data = data.replace([np.inf, -np.inf], np.nan)

# Remove columns that contain no usable information.
data = data.dropna(axis=1, how="all")

numeric_columns = data.select_dtypes(
    include=np.number
).columns.tolist()

if len(numeric_columns) < 2:
    st.error(
        "At least two usable numeric columns are required: "
        "one target and at least one feature."
    )
    st.stop()


# --------------------------------------------------
# SELECT TARGET
# --------------------------------------------------

st.subheader("🎯 Configure Prediction")

preferred_targets = [
    column for column in numeric_columns
    if any(
        word in str(column).lower()
        for word in ["temperature", "rainfall", "precipitation", "humidity"]
    )
]

default_target = (
    preferred_targets[0]
    if preferred_targets
    else numeric_columns[0]
)

target = st.selectbox(
    "Select the value you want to predict",
    numeric_columns,
    index=numeric_columns.index(default_target)
)

candidate_features = [
    column for column in numeric_columns
    if column != target
]

selected_features = st.multiselect(
    "Select input features",
    candidate_features,
    default=candidate_features
)

if not selected_features:
    st.warning("Select at least one input feature.")
    st.stop()


# --------------------------------------------------
# PREPARE TRAINING DATA
# --------------------------------------------------

model_data = data[selected_features + [target]].copy()

# Keep rows where the target is known.
model_data = model_data.dropna(subset=[target])

# Exclude rows with invalid target values.
model_data = model_data[
    np.isfinite(model_data[target])
]

if len(model_data) < 10:
    st.error(
        "At least 10 usable records are required for this demonstration. "
        "More records are recommended for reliable evaluation."
    )
    st.stop()

X = model_data[selected_features]
y = model_data[target]

if y.nunique() < 2:
    st.error("The selected target contains no meaningful variation.")
    st.stop()


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

test_fraction = st.slider(
    "Percentage of data reserved for testing",
    min_value=10,
    max_value=40,
    value=20,
    step=5
)

random_seed = 42

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=test_fraction / 100,
    random_state=random_seed
)

st.write(f"Training records: **{len(X_train)}**")
st.write(f"Testing records: **{len(X_test)}**")


# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

st.subheader("🤖 Train and Compare Models")

models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=random_seed
    ),
    "Extra Trees": ExtraTreesRegressor(
        n_estimators=200,
        random_state=random_seed
    )
}

if st.button("🚀 Train Models", type="primary"):

    results = []
    fitted_models = {}

    progress = st.progress(0)

    for index, (name, estimator) in enumerate(models.items()):

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", estimator)
        ])

        try:
            pipeline.fit(X_train, y_train)

            predictions = pipeline.predict(X_test)

            mae = mean_absolute_error(y_test, predictions)

            rmse = np.sqrt(
                mean_squared_error(y_test, predictions)
            )

            r2 = (
                r2_score(y_test, predictions)
                if len(y_test) >= 2
                else np.nan
            )

            results.append({
                "Model": name,
                "MAE": mae,
                "RMSE": rmse,
                "R2": r2
            })

            fitted_models[name] = pipeline

        except Exception as error:
            st.warning(f"{name} could not be trained: {error}")

        progress.progress((index + 1) / len(models))

    if not results:
        st.error("No models could be trained.")
        st.stop()

    results_df = pd.DataFrame(results).sort_values(
        "MAE",
        ascending=True
    )

    # Save fitted models and evaluation data for subsequent interactions.
    st.session_state["weather_ml_results"] = results_df
    st.session_state["weather_ml_models"] = fitted_models
    st.session_state["weather_ml_X_test"] = X_test
    st.session_state["weather_ml_y_test"] = y_test
    st.session_state["weather_ml_target"] = target
    st.session_state["weather_ml_features"] = selected_features

    st.success("Model training completed!")


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "weather_ml_results" in st.session_state:

    results_df = st.session_state["weather_ml_results"]

    if st.session_state.get("weather_ml_target") != target:
        st.info("Train the models again after changing the target.")
    elif st.session_state.get("weather_ml_features") != selected_features:
        st.info("Train the models again after changing the features.")
    else:

        st.subheader("📊 Model Performance")

        st.dataframe(
            results_df.round(4),
            use_container_width=True,
            hide_index=True
        )

        best_model_name = results_df.iloc[0]["Model"]

        best_model = st.session_state[
            "weather_ml_models"
        ][best_model_name]

        st.success(
            f"Best model by test MAE: **{best_model_name}**"
        )

        st.caption(
            "Lower MAE and RMSE indicate smaller prediction errors. "
            "Higher R² is generally better, but R² can be negative."
        )

        # Actual versus predicted chart.
        X_test_saved = st.session_state["weather_ml_X_test"]
        y_test_saved = st.session_state["weather_ml_y_test"]

        predictions = best_model.predict(X_test_saved)

        comparison_df = pd.DataFrame({
            "Actual": y_test_saved.to_numpy(),
            "Predicted": predictions
        })

        st.subheader("📈 Actual vs Predicted")

        fig = px.scatter(
            comparison_df,
            x="Actual",
            y="Predicted",
            title=f"Actual vs Predicted — {best_model_name}",
            hover_data=["Actual", "Predicted"]
        )

        st.plotly_chart(fig, use_container_width=True)

        comparison_df["Error"] = (
            comparison_df["Actual"] -
            comparison_df["Predicted"]
        )

        st.download_button(
            "⬇️ Download Test Predictions",
            data=comparison_df.to_csv(index=False).encode("utf-8"),
            file_name="weather_test_predictions.csv",
            mime="text/csv"
        )

        # Predict using a new row of input values.
        st.subheader("🔮 Predict a Weather Measurement")

        st.write(
            "Enter values for the selected input features. "
            "Use the same units as your training dataset."
        )

        input_values = {}

        input_columns = st.columns(
            min(3, len(selected_features))
        )

        for index, feature in enumerate(selected_features):

            valid_values = pd.to_numeric(
                X[feature],
                errors="coerce"
            ).dropna()

            default_value = (
                float(valid_values.median())
                if not valid_values.empty
                else 0.0
            )

            with input_columns[index % len(input_columns)]:
                input_values[feature] = st.number_input(
                    feature,
                    value=default_value,
                    format="%.4f",
                    key=f"weather_input_{feature}"
                )

        if st.button("Predict Weather Value"):

            input_df = pd.DataFrame(
                [input_values],
                columns=selected_features
            )

            prediction = best_model.predict(input_df)[0]

            st.metric(
                f"Predicted {target}",
                f"{prediction:.2f}"
            )

            st.caption(
                "This prediction is an estimate based on historical "
                "relationships in the uploaded dataset."
            )

else:
    st.info(
        "Choose a target and features, then click Train Models "
        "to see the evaluation results."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Educational machine-learning demonstration. "
    "Model performance depends on data quality, dataset size, "
    "feature selection, and whether the test data represents "
    "the intended prediction task."
)
