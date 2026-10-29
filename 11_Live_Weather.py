
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

from datetime import datetime
from utils.style import apply_custom_style

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Live Weather",
    page_icon="🌦️",
    layout="wide"
)

apply_custom_style()


st.title("🌦️ Live Weather Dashboard")

st.write(
    "Search for a city to view current weather conditions "
    "and the upcoming seven-day forecast."
)

st.divider()

# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# --------------------------------------------------
# CITY SEARCH
# --------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def search_city(city_name):
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city_name,
            "count": 10,
            "language": "en",
            "format": "json"
        },
        timeout=15
    )

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# FETCH WEATHER
# --------------------------------------------------

@st.cache_data(ttl=900, show_spinner=False)
def fetch_weather(latitude, longitude, timezone):
    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum,"
                "wind_speed_10m_max"
            ),
            "forecast_days": 7,
            "timezone": timezone
        },
        timeout=20
    )

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# WEATHER DESCRIPTION
# --------------------------------------------------

def weather_description(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    }

    return descriptions.get(code, "Weather conditions unavailable")


# --------------------------------------------------
# CITY INPUT
# --------------------------------------------------

st.subheader("🔍 Search for a City")

with st.form("city_search_form"):
    city_name = st.text_input(
        "Enter city name",
        value="Amalapuram",
        placeholder="Example: Hyderabad"
    )

    search_button = st.form_submit_button(
        "Get Live Weather",
        type="primary"
    )


if search_button:
    if not city_name.strip():
        st.warning("Please enter a city name.")
        st.stop()

    try:
        with st.spinner("Searching for the city..."):
            city_data = search_city(city_name.strip())

        locations = city_data.get("results", [])

        if not locations:
            st.error(
                "City not found. Check the spelling or try "
                "adding the state or country."
            )
            st.stop()

        # Store results so they remain visible on reruns
        st.session_state["live_weather_locations"] = locations
        st.session_state["live_weather_search"] = city_name.strip()

    except requests.RequestException as error:
        st.error(f"Could not search for the city: {error}")
        st.stop()


# --------------------------------------------------
# SELECT LOCATION
# --------------------------------------------------

locations = st.session_state.get(
    "live_weather_locations",
    []
)

if not locations:
    st.info(
        "Enter a city name and click Get Live Weather "
        "to begin."
    )
    st.stop()

location_labels = []

for location in locations:
    label_parts = [
        location.get("name", "Unknown location"),
        location.get("admin1", ""),
        location.get("country", "")
    ]

    label = ", ".join(
        part for part in label_parts if part
    )

    location_labels.append(label)


selected_index = st.selectbox(
    "Choose the correct location",
    range(len(locations)),
    format_func=lambda i: location_labels[i]
)

selected_location = locations[selected_index]

latitude = selected_location["latitude"]
longitude = selected_location["longitude"]
timezone = selected_location.get("timezone", "auto")

st.caption(
    f"Coordinates: {latitude:.4f}, {longitude:.4f}"
)

# --------------------------------------------------
# GET WEATHER DATA
# --------------------------------------------------

try:
    with st.spinner("Loading weather information..."):
        weather_data = fetch_weather(
            latitude,
            longitude,
            timezone
        )

except requests.RequestException as error:
    st.error(f"Could not retrieve weather data: {error}")
    st.stop()

current = weather_data.get("current", {})
daily = weather_data.get("daily", {})

if not current or not daily:
    st.error(
        "The weather service did not return the expected data."
    )
    st.stop()


# --------------------------------------------------
# CURRENT WEATHER
# --------------------------------------------------

st.divider()

st.subheader(
    f"📍 Current Weather — {selected_location.get('name', 'Selected City')}"
)

temperature = current.get("temperature_2m")
humidity = current.get("relative_humidity_2m")
wind_speed = current.get("wind_speed_10m")
precipitation = current.get("precipitation")
weather_code = current.get("weather_code")

weather_text = weather_description(weather_code)

st.markdown(f"### {weather_text}")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🌡️ Temperature",
    f"{temperature} °C" if temperature is not None else "N/A"
)

c2.metric(
    "💧 Humidity",
    f"{humidity}%" if humidity is not None else "N/A"
)

c3.metric(
    "💨 Wind Speed",
    f"{wind_speed} km/h" if wind_speed is not None else "N/A"
)

c4.metric(
    "🌧️ Precipitation",
    f"{precipitation} mm" if precipitation is not None else "N/A"
)

st.caption(
    f"Observation time: {current.get('time', 'Unavailable')} "
    f"({timezone})"
)

st.caption(
    "Data source: Open-Meteo. Conditions are model-based "
    "weather data and may differ from local observations."
)


# --------------------------------------------------
# SEVEN-DAY FORECAST
# --------------------------------------------------

st.divider()
st.subheader("📅 Seven-Day Weather Forecast")

forecast_df = pd.DataFrame({
    "Date": daily.get("time", []),
    "Weather Code": daily.get("weather_code", []),
    "Maximum Temperature (°C)": daily.get(
        "temperature_2m_max", []
    ),
    "Minimum Temperature (°C)": daily.get(
        "temperature_2m_min", []
    ),
    "Precipitation (mm)": daily.get(
        "precipitation_sum", []
    ),
    "Maximum Wind Speed (km/h)": daily.get(
        "wind_speed_10m_max", []
    )
})

if not forecast_df.empty:
    forecast_df["Weather"] = forecast_df["Weather Code"].apply(
        lambda code: weather_description(code)
        if pd.notna(code)
        else "Unavailable"
    )

    st.dataframe(
        forecast_df[
            [
                "Date",
                "Weather",
                "Maximum Temperature (°C)",
                "Minimum Temperature (°C)",
                "Precipitation (mm)",
                "Maximum Wind Speed (km/h)"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # TEMPERATURE CHART
    # --------------------------------------------------

    st.subheader("📈 Forecast Temperature Trend")

    chart_df = forecast_df.melt(
        id_vars=["Date"],
        value_vars=[
            "Maximum Temperature (°C)",
            "Minimum Temperature (°C)"
        ],
        var_name="Temperature Type",
        value_name="Temperature (°C)"
    )

    fig = px.line(
        chart_df,
        x="Date",
        y="Temperature (°C)",
        color="Temperature Type",
        markers=True,
        title="Daily Minimum and Maximum Temperature"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # PRECIPITATION CHART
    # --------------------------------------------------

    st.subheader("🌧️ Forecast Precipitation")

    rain_fig = px.bar(
        forecast_df,
        x="Date",
        y="Precipitation (mm)",
        title="Expected Daily Precipitation"
    )

    st.plotly_chart(
        rain_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # DOWNLOAD FORECAST
    # --------------------------------------------------

    csv_data = forecast_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Seven-Day Forecast",
        data=csv_data,
        file_name="seven_day_weather_forecast.csv",
        mime="text/csv"
    )

else:
    st.warning("No forecast records were returned.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Weather Data Analysis System | Live Weather Module"
)

st.markdown(
    "Weather data provided by "
    "[Open-Meteo](https://open-meteo.com/). "
    "Location search uses its geocoding service."
)

