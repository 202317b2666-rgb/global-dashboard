import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide"
)

st.title("🌍 Global Health Dashboard")

# ---------------------------------
# Load data
# ---------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    data = pd.read_csv(os.path.join(BASE_DIR, "final_with_socio_cleaned.csv"))
    hex_df = pd.read_csv(os.path.join(BASE_DIR, "Hex.csv"))

    with open(os.path.join(BASE_DIR, "countries.geo.json"), "r", encoding="utf-8") as f:
        geojson = json.load(f)

    return data, hex_df, geojson


data, hex_df, geojson = load_data()
st.success("Data loaded successfully ✅")

# ---------------------------------
# Clean columns
# ---------------------------------
data.columns = data.columns.str.strip()

# ---------------------------------
# Detect ISO column
# ---------------------------------
if "ISO3" in data.columns:
    iso_col = "ISO3"
elif "ISO3_code" in data.columns:
    iso_col = "ISO3_code"
elif "iso_alpha" in data.columns:
    iso_col = "iso_alpha"
else:
    st.error("❌ ISO country code column not found")
    st.stop()

# ---------------------------------
# Sidebar controls
# ---------------------------------
st.sidebar.header("🌐 Controls")

year_min = int(data["Year"].min())
year_max = int(data["Year"].max())

selected_year = st.sidebar.slider(
    "Select Year",
    min_value=year_min,
    max_value=year_max,
    value=2020
)

country_list = sorted(data[iso_col].dropna().unique())
selected_country = st.sidebar.selectbox("Select Country", country_list)

metric = st.sidebar.selectbox(
    "Select Metric",
    [c for c in data.columns if c not in [iso_col, "Location", "Country", "Year"]]
)

# ---------------------------------
# Filter data
# ---------------------------------
year_df = data[data["Year"] == selected_year]
country_df = data[data[iso_col] == selected_country]

# ---------------------------------
# World map
# ---------------------------------
fig = px.choropleth(
    year_df,
    geojson=geojson,
    locations=iso_col,
    color=metric,
    hover_name="Location" if "Location" in data.columns else iso_col,
    color_continuous_scale="Viridis",
    projection="natural earth"
)

fig.update_geos(
    showcountries=True,
    showcoastlines=True,
    fitbounds="locations"
)

fig.update_layout(
    height=600,
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------
# COUNTRY DETAILS (Popup-like panel)
# ---------------------------------
st.markdown("## 📊 Country Details")

with st.expander(f"📌 View details for {selected_country}", expanded=True):

    latest_row = country_df[country_df["Year"] == selected_year]

    if not latest_row.empty:
        st.markdown("### 🧾 Snapshot")

        cols = st.columns(3)
        for i, col in enumerate(latest_row.columns):
            if col not in [iso_col, "Year", "Location", "Country"]:
                cols[i % 3].metric(col, round(float(latest_row[col]), 2))

    st.markdown("### 📈 Trend Over Time")

    trend_fig = px.line(
        country_df.sort_values("Year"),
        x="Year",
        y=metric,
        markers=True,
        title=f"{metric} Trend ({selected_country})"
    )

    st.plotly_chart(trend_fig, use_container_width=True)
