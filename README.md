# Weather Data Analysis System

## 1. Project Overview

The Weather Data Analysis System is a Python-based application designed to analyze weather datasets, visualize weather patterns, clean data, and demonstrate machine-learning techniques.

The application provides an interactive interface for exploring measurements such as temperature, humidity, rainfall, and wind speed.

## 2. Objectives

* Analyze weather data using Python.
* Upload and explore CSV datasets.
* Identify and handle missing values and duplicate records.
* Calculate statistical summaries of weather measurements.
* Visualize weather trends and comparisons.
* Demonstrate machine-learning regression.
* Generate downloadable CSV and PDF reports.

## 3. Technologies Used

| Technology   | Purpose                      |
| ------------ | ---------------------------- |
| Python       | Main programming language    |
| Streamlit    | Interactive web application  |
| Pandas       | Data processing and analysis |
| NumPy        | Numerical operations         |
| Matplotlib   | Charts and plots             |
| Seaborn      | Statistical visualization    |
| Plotly       | Interactive charts           |
| Scikit-learn | Machine-learning models      |
| ReportLab    | PDF report generation        |

## 4. Main Features

### Dashboard

Displays dataset information and weather summary metrics.

### Dataset Upload

Allows users to load a sample dataset or upload a CSV file.

### Data Cleaning

Demonstrates handling missing values and duplicate records.

### Weather Analysis

Calculates descriptive statistics for numeric weather measurements.

### Visualizations

Displays weather trends, comparisons, and other charts supported by the dataset.

### Reports

Presents data summaries and downloadable results.

### Machine Learning

Demonstrates regression using a Random Forest model and evaluation metrics.

### Weather Prediction

Allows users to enter selected numeric measurements and estimate a target value using a trained regression model.

### PDF Reports

Generates a downloadable PDF containing dataset information, available statistics, and optional charts.

## 5. Project Structure

```text
WeatherDataAnalysis/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
├── pages/
└── utils/
```

## 6. Installation

Install Python and open the project folder in VS Code.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 7. Run the Application

From the project folder, execute:

```bash
python -m streamlit run app.py
```

Open the local address displayed in the terminal.

## 8. Dataset

The application supports CSV datasets containing suitable weather measurements.

Common columns include:

* Date
* City
* Temperature
* Humidity
* Rainfall
* Wind_Speed

Column names and measurement units may vary between datasets. Some pages require specific column names.

Any sample dataset should be identified as sample or demonstration data rather than verified meteorological observations.

## 9. Machine-Learning Limitations

The machine-learning components demonstrate regression using available dataset features.

Prediction quality depends on dataset size, data quality, feature selection, and the relationship between the input features and target variable.

These demonstrations should not be treated as reliable operational weather forecasts without appropriate time-based validation, suitable historical observations, and a dedicated forecasting methodology.

## 10. Future Enhancements

* Secure user authentication and role-based access.
* Live weather data integration through a weather API.
* Improved date-range filtering.
* More advanced forecasting algorithms.
* Model saving and model evaluation.
* Automated report scheduling.
* Database integration.
* Cloud deployment.

## 11. Conclusion

The Weather Data Analysis System demonstrates how Python data-analysis libraries, interactive visualizations, and machine-learning techniques can be combined in a web application.

It provides a practical learning project for understanding weather data processing, exploratory data analysis, visualization, and basic regression.

## 12. Disclaimer

This project is intended for educational and demonstration purposes. Predictions generated from small or unsuitable datasets may be inaccurate.


## Professional multi-page theme
All Streamlit pages use the shared visual theme in `utils/style.py`. The theme provides a navy sidebar, blue active navigation, light analytics workspace, KPI cards, rounded chart panels, and consistent styling for tables, forms, tabs, and file uploads. Login is not required; launch the app with `python -m streamlit run app.py`.
