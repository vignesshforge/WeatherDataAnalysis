import streamlit as st
from utils.style import apply_custom_style

st.set_page_config(
    page_title="Weather Data Analysis",
    page_icon="🌦️",
    layout="wide",
)

apply_custom_style()

st.markdown("""
<div class="weather-hero">
  <div class="eyebrow">Weather analytics platform</div>
  <h1>Weather Insights</h1>
  <p>Explore weather data, discover patterns, and make smarter decisions.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Your weather workspace")
st.markdown('<p class="section-note">Choose a workflow below or use the navigation menu to open any module.</p>', unsafe_allow_html=True)
a,b,c=st.columns(3)
with a:
    st.markdown('<div class="mini-card"><h3>📊 Analyze</h3><p>Summarize temperature, humidity, rainfall and wind-speed measurements.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.page_link("pages/1_Dashboard.py", label="Open dashboard", icon="🏠", use_container_width=True)
with b:
    st.markdown('<div class="mini-card"><h3>🌤️ Live weather</h3><p>Search for a city and explore current conditions and a seven-day forecast.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.page_link("pages/11_Live_Weather.py", label="Check live weather", icon="🌦️", use_container_width=True)
with c:
    st.markdown('<div class="mini-card"><h3>🤖 Predict</h3><p>Train and compare models using your uploaded historical weather data.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.page_link("pages/8_Improved_Weather_Prediction.py", label="Open ML prediction", icon="🤖", use_container_width=True)

st.divider()
st.subheader("Recommended workflow")
cols=st.columns(4)
for col, title, desc in zip(cols,["01 · Upload","02 · Clean","03 · Explore","04 · Report"],["Load a CSV dataset","Handle missing values","Visualize trends","Export findings"]):
    with col:
        st.markdown(f'<div class="mini-card"><div class="eyebrow">{title}</div><p>{desc}</p></div>',unsafe_allow_html=True)
st.caption("Weather Data Analysis System · Academic project")
