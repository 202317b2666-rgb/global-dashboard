import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="World Map Dashboard", layout="wide")

# ---------------------------
# LOAD FILES
# ---------------------------

# Load HEX.csv
hex_df = pd.read_csv("HEX.csv")

# Load GeoJSON
with open("countries.geo.json", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# ---------------------------
# HEADER
# ---------------------------
st.title("🌍 Interactive World Map Dashboard")
st.write("This map is built using HEX.csv + countries.geo.json")

# ---------------------------
# PLOT MAP USING PLOTLY
# ---------------------------

fig = px.choropleth(
    hex_df,
    geojson=geojson_data,
    locations="Code",       # ISO3 code from HEX.csv
    color="Color",          # HEX color from HEX.csv
    featureidkey="properties.ISO_A3",  # ISO3 inside GeoJSON
    projection="natural earth"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(height=700, margin={"r":0, "t":30, "l":0, "b":0})

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# SHOW DATA TABLE
# ---------------------------
st.subheader("HEX Color Mapping Table")
st.dataframe(hex_df)

