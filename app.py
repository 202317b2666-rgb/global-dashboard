import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Country Dashboard",
    layout="wide"
)

st.title("🌍 Country Dashboard")

# -----------------------------
# Load data safely
# -----------------------------
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

# -----------------------------
# Clean column names
# -----------------------------
data.columns = data.columns.str.strip()
hex_df.columns = hex_df.columns.str.strip()

# -----------------------------
# Detect ISO column automatically
# -----------------------------
if "ISO3" in data.columns:
    iso_col = "ISO3"
elif "iso_alpha" in data.columns:
    iso_col = "iso_alpha"
elif "ISO3_code" in data.columns:
    iso_col = "ISO3_code"
else:
    st.error("❌ No ISO country code column found in dataset")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("🌐 Controls")

country_list = ["All"] + sorted(data[iso_col].dropna().unique())
selected_country = st.sidebar.selectbox(
    "Select Country",
    country_list
)

metric = st.sidebar.selectbox(
    "Select Metric",
    [col for col in data.columns if col not in [iso_col, "Location", "Country", "Year"]]
)

# -----------------------------
# Filter data
# -----------------------------
if selected_country == "All":
    filtered = data.copy()
else:
    filtered = data[data[iso_col] == selected_country]

# -----------------------------
# Merge colors
# -----------------------------
if "hex" in hex_df.columns:
    color_col = "hex"
elif "HEX" in hex_df.columns:
    color_col = "HEX"
else:
    color_col = None

if color_col:
    filtered = filtered.merge(
        hex_df[[iso_col, color_col]],
        on=iso_col,
        how="left"
    )

# -----------------------------
# World Map
# -----------------------------
fig = px.choropleth(
    filtered,
    geojson=geojson,
    locations=iso_col,
    color=metric,
    hover_name="Location" if "Location" in filtered.columns else iso_col,
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

# -----------------------------
# Country Details (popup-style section)
# -----------------------------
st.subheader("📊 Country Details")

if selected_country != "All":
    st.dataframe(filtered)
else:
    st.info("Select a country to view detailed data")

