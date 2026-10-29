import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show_temperature_trend(df, date_column, temperature_column):
    """Display an interactive temperature trend chart."""

    if df.empty:
        st.info("No data available to display.")
        return

    data = df.copy()
    data[date_column] = pd.to_datetime(
        data[date_column], errors="coerce"
    )
    data[temperature_column] = pd.to_numeric(
        data[temperature_column], errors="coerce"
    )
    data = data.dropna(
        subset=[date_column, temperature_column]
    ).sort_values(date_column)

    if data.empty:
        st.warning("No valid temperature data was found.")
        return

    fig = px.line(
        data,
        x=date_column,
        y=temperature_column,
        markers=True,
        title="Temperature Trend",
        template="plotly_white",
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title="Date",
        yaxis_title="Temperature",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


def show_humidity_trend(df, date_column, humidity_column):
    """Display an interactive humidity trend chart."""

    if df.empty:
        st.info("No data available to display.")
        return

    data = df.copy()
    data[date_column] = pd.to_datetime(
        data[date_column], errors="coerce"
    )
    data[humidity_column] = pd.to_numeric(
        data[humidity_column], errors="coerce"
    )
    data = data.dropna(
        subset=[date_column, humidity_column]
    ).sort_values(date_column)

    if data.empty:
        st.warning("No valid humidity data was found.")
        return

    fig = px.area(
        data,
        x=date_column,
        y=humidity_column,
        title="Humidity Trend",
        template="plotly_white",
    )

    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title="Date",
        yaxis_title="Humidity (%)",
    )

    st.plotly_chart(fig, use_container_width=True)


def show_city_temperature_comparison(
    df, city_column, temperature_column
):
    """Compare average temperatures across cities."""

    if df.empty:
        st.info("No data available to display.")
        return

    data = df.copy()
    data[temperature_column] = pd.to_numeric(
        data[temperature_column], errors="coerce"
    )
    data = data.dropna(subset=[city_column, temperature_column])

    summary = (
        data.groupby(city_column, as_index=False)[temperature_column]
        .mean()
        .sort_values(temperature_column, ascending=False)
    )

    if summary.empty:
        st.warning("No valid temperature data was found.")
        return

    fig = px.bar(
        summary,
        x=city_column,
        y=temperature_column,
        color=city_column,
        title="Average Temperature by City",
        template="plotly_white",
    )

    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title="City",
        yaxis_title="Average Temperature",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)