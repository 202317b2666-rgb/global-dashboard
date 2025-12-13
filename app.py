# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# Ensure all files are loaded relative to this script
BASE_DIR = os.path.dirname(__file__)

@st.cache_data
def load_data():
    # Load cleaned socio-economic data
    df = pd.read_csv(os.path.join(BASE_DIR, "final_with_socio_cleaned.csv"))
    
    # Load GeoJSON for countries
    with open(os.path.join(BASE_DIR, "countries.geo.json")) as f:
        geojson = json.load(f)
    
    # Load HEX color mapping
    hex_df = pd.read_csv(os.path.join(BASE_DIR, "Hex.csv"))
    
    return df, geojson, hex_df

# Load datasets
data, geojson, hex_df = load_data()

st.title("🌍 Global Health & Demographics Dashboard")

# Country selection
country_list = [""] + sorted(data['ISO3'].unique())
selected_country = st.selectbox("Select a Country", country_list)

# Filter data if a country is selected
if selected_country:
    country_data = data[data['ISO3'] == selected_country]
else:
    country_data = data.copy()

# Example Plotly map
fig = px.choropleth(
    country_data,
    geojson=geojson,
    locations="ISO3",
    color="HDI",  # Example: Human Development Index
    hover_name="Location",
    color_continuous_scale="Viridis"
)
fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)

# Optional: show HEX color mapping
if st.checkbox("Show HEX color mapping"):
    st.dataframe(hex_df)
