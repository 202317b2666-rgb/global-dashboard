# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Title
st.title("🌍 Interactive World Map Dashboard")
st.markdown("This map is built using HEX.csv + countries.geo.json")

# Load CSV
hex_df = pd.read_csv("HEX.csv")

# Clean CSV: fill missing figma_hex with default color
hex_df["figma_hex"] = hex_df["figma_hex"].fillna("#808080")  # gray for missing

# Add color key
hex_df["color_key"] = hex_df["figma_hex"]

# Load GeoJSON
with open("countries.geo.json", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Create choropleth
fig = px.choropleth(
    hex_df,
    geojson=geojson_data,
    locations="iso_alpha",
    color="color_key",
    hover_name="country",
    color_discrete_map="identity",
    projection="natural earth",
)

fig.update_geos(
    showcountries=True, countrycolor="black",
    showcoastlines=True, coastlinecolor="gray",
    showland=True, landcolor="lightgray",
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=600,
)

# Show figure
st.plotly_chart(fig, use_container_width=True)
