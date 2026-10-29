import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import load_dataset
from utils.style import apply_custom_style

st.set_page_config(page_title="Weather Insights Dashboard", page_icon="🌦️", layout="wide")
apply_custom_style()

# ---------- Data ----------
df = load_dataset()

st.markdown("""
<div class="weather-hero dashboard-hero">
  <div class="hero-topline"><span class="eyebrow">WEATHER INTELLIGENCE · OVERVIEW</span><span class="hero-status">● DATA WORKSPACE</span></div>
  <h1>Weather Insights</h1>
  <p>Understand local conditions, compare locations, and discover patterns in your weather data.</p>
</div>
""", unsafe_allow_html=True)

if df is None or df.empty:
    st.markdown("""
    <div class="empty-state"><div class="empty-icon">☁️</div><h3>Your weather dashboard is ready</h3>
    <p>Upload a CSV dataset to populate the metrics, charts, and location comparisons.</p></div>
    """, unsafe_allow_html=True)
    if st.button("📂 Go to Upload Dataset", type="primary"):
        st.switch_page("pages/2_Upload_Dataset.py")
    st.stop()

# Normalize column names and detect common variants.
df = df.copy()
df.columns = [str(c).strip() for c in df.columns]
colmap = {str(c).lower().strip().replace(" ", "_").replace("-", "_"): c for c in df.columns}

def find_col(*names):
    for name in names:
        if name in colmap:
            return colmap[name]
    return None

temp_col = find_col("temperature", "temp", "temperature_c", "temp_c", "temperature_2m")
humidity_col = find_col("humidity", "relative_humidity", "relative_humidity_2m")
rain_col = find_col("rainfall", "rain", "precipitation", "precipitation_sum", "rain_mm")
wind_col = find_col("wind_speed", "windspeed", "wind", "wind_speed_10m", "wind_speed_kmh")
city_col = find_col("city", "location", "place", "town")
date_col = find_col("date", "datetime", "timestamp", "time")

for c in [temp_col, humidity_col, rain_col, wind_col]:
    if c:
        df[c] = pd.to_numeric(df[c], errors="coerce")
if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ---------- Filters ----------
st.markdown('<div class="section-heading"><div><span class="section-kicker">EXPLORE</span><h2>Dashboard controls</h2></div><span class="section-helper">All insights update with your filters</span></div>', unsafe_allow_html=True)
with st.container(border=True):
    f1, f2, f3 = st.columns([1.1, 1.7, 1])
    filtered = df.copy()
    if city_col:
        city_values = sorted(filtered[city_col].dropna().astype(str).unique().tolist())
        with f1:
            selected_cities = st.multiselect("Location", city_values, default=city_values, placeholder="Choose cities")
        filtered = filtered[filtered[city_col].astype(str).isin(selected_cities)]
    else:
        with f1:
            st.caption("No city/location column found")
    if date_col and filtered[date_col].notna().any():
        valid_dates = filtered[date_col].dropna()
        min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
        with f2:
            chosen = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(chosen, (tuple, list)) and len(chosen) == 2:
            start, end = chosen
            filtered = filtered[filtered[date_col].dt.date.between(start, end)]
    else:
        with f2:
            st.caption("Add a Date column to enable date filtering")
    with f3:
        st.markdown("<div class='filter-info-label'>ACTIVE DATASET</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='filter-info-value'>{len(df):,} <span>rows</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='filter-info-sub'>Showing {len(filtered):,} matching rows</div>", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No records match the selected filters. Try selecting another city or date range.")
    st.stop()

# ---------- KPI cards ----------
st.markdown('<div class="section-heading"><div><span class="section-kicker">AT A GLANCE</span><h2>Weather summary</h2></div><span class="section-helper">Calculated from the selected records</span></div>', unsafe_allow_html=True)

def metric_value(column, suffix="", aggregate="mean", digits=1):
    if not column or column not in filtered.columns:
        return "—"
    values = pd.to_numeric(filtered[column], errors="coerce")
    if values.notna().sum() == 0:
        return "—"
    value = values.sum(min_count=1) if aggregate == "sum" else values.mean()
    return f"{value:,.{digits}f}{suffix}"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-top'><span class='kpi-icon temp-icon'>☀</span><span class='kpi-tag'>TEMPERATURE</span></div><div class='kpi-label'>Average temperature</div><div class='kpi-value'>{metric_value(temp_col, '°C')}</div><div class='kpi-foot'>Mean across selected records</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-top'><span class='kpi-icon humidity-icon'>◉</span><span class='kpi-tag'>HUMIDITY</span></div><div class='kpi-label'>Average humidity</div><div class='kpi-value'>{metric_value(humidity_col, '%', digits=0)}</div><div class='kpi-foot'>Relative humidity</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-top'><span class='kpi-icon wind-icon'>≋</span><span class='kpi-tag'>WIND</span></div><div class='kpi-label'>Average wind speed</div><div class='kpi-value'>{metric_value(wind_col, ' km/h')}</div><div class='kpi-foot'>Based on available observations</div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-top'><span class='kpi-icon rain-icon'>♧</span><span class='kpi-tag'>PRECIPITATION</span></div><div class='kpi-label'>Total rainfall</div><div class='kpi-value'>{metric_value(rain_col, ' mm', 'sum')}</div><div class='kpi-foot'>Sum across selected records</div></div>", unsafe_allow_html=True)

# ---------- Main charts ----------
chart_left, chart_right = st.columns([1.35, 1], gap="large")
with chart_left:
    st.markdown('<div class="panel-title"><div><span class="panel-icon">↗</span><span>Temperature trend</span></div><span class="panel-subtitle">Over time</span></div>', unsafe_allow_html=True)
    if temp_col and date_col:
        chart = filtered[[date_col, temp_col] + ([city_col] if city_col else [])].dropna(subset=[date_col, temp_col]).sort_values(date_col)
        if not chart.empty:
            fig = px.line(chart, x=date_col, y=temp_col, color=city_col if city_col else None, markers=True,
                          labels={date_col: "Date", temp_col: "Temperature (°C)", city_col: "Location" if city_col else ""})
            fig.update_traces(line=dict(width=3), marker=dict(size=7))
            fig.update_layout(height=340, margin=dict(l=8, r=8, t=18, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Inter, sans-serif", color="#536784", size=12), legend_title_text="Location", hovermode="x unified")
            fig.update_xaxes(showgrid=False, linecolor="#dce6f3")
            fig.update_yaxes(showgrid=True, gridcolor="#edf2f9", zeroline=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No valid date-temperature pairs are available for the selected filters.")
    else:
        st.info("A recognizable Date and Temperature column are needed for this chart.")

with chart_right:
    st.markdown('<div class="panel-title"><div><span class="panel-icon rain-panel-icon">☂</span><span>Rainfall overview</span></div><span class="panel-subtitle">By date</span></div>', unsafe_allow_html=True)
    if rain_col and date_col:
        rain = filtered[[date_col, rain_col] + ([city_col] if city_col else [])].dropna(subset=[date_col, rain_col]).sort_values(date_col)
        if not rain.empty:
            fig2 = px.bar(rain, x=date_col, y=rain_col, color=city_col if city_col else None,
                          labels={date_col: "Date", rain_col: "Rainfall (mm)", city_col: "Location" if city_col else ""}, barmode="group")
            fig2.update_layout(height=340, margin=dict(l=8, r=8, t=18, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font=dict(family="Inter, sans-serif", color="#536784", size=12), legend_title_text="Location")
            fig2.update_xaxes(showgrid=False, linecolor="#dce6f3")
            fig2.update_yaxes(showgrid=True, gridcolor="#edf2f9", zeroline=False)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No rainfall values are available for the selected filters.")
    elif rain_col:
        st.metric("Total rainfall", metric_value(rain_col, " mm", "sum"))
    else:
        st.info("No rainfall column was detected in this dataset.")

# ---------- Secondary analytics ----------
if city_col and temp_col:
    st.markdown('<div class="section-heading"><div><span class="section-kicker">COMPARE</span><h2>Location performance</h2></div><span class="section-helper">Average temperature by location</span></div>', unsafe_allow_html=True)
    city_stats = filtered.groupby(city_col, dropna=True)[temp_col].mean().reset_index().dropna().sort_values(temp_col, ascending=True)
    if not city_stats.empty:
        fig3 = px.bar(city_stats, x=temp_col, y=city_col, orientation="h", color=temp_col, color_continuous_scale=[[0, "#b8d8ff"], [1, "#2678f3"]],
                      labels={city_col: "Location", temp_col: "Average temperature (°C)"}, text_auto=".1f")
        fig3.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
        fig3.update_layout(height=max(220, min(420, 42 * len(city_stats))), margin=dict(l=8, r=35, t=10, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(family="Inter, sans-serif", color="#536784", size=12), coloraxis_showscale=False)
        fig3.update_xaxes(showgrid=True, gridcolor="#edf2f9", zeroline=False)
        fig3.update_yaxes(showgrid=False, title=None)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# ---------- Dataset table and export ----------
with st.expander("📋 View and export filtered records", expanded=False):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download filtered data (CSV)", filtered.to_csv(index=False).encode("utf-8"), "weather_dashboard_filtered.csv", "text/csv", type="primary")

st.markdown('<div class="dashboard-footer">WEATHER INSIGHTS <span>•</span> Analytics generated from the selected dataset. Verify units and data quality before using results for decisions.</div>', unsafe_allow_html=True)
