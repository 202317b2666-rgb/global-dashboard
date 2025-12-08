import json
import pandas as pd
import plotly.express as px
import streamlit as st

# --- Page config ---
st.set_page_config(page_title="🌍 Interactive World Map Dashboard", layout="wide")

# --- Load GeoJSON ---
with open("countries.geo.json", "r", encoding="utf-8") as f:
    world_geojson = json.load(f)

# --- Load HEX colors ---
hex_df = pd.read_csv("HEX.csv")  # columns: country, iso_alpha, figma_hex

# Make a color column for Plotly
hex_df["color_key"] = hex_df["figma_hex"]

# --- Build the choropleth map ---
fig = px.choropleth(
    hex_df,
    geojson=world_geojson,
    locations="iso_alpha",         # ISO code column
    featureidkey="id",             # match GeoJSON 'id'
    color="color_key",             # your HEX colors
    hover_name="country",          # show country name on hover
    color_discrete_map="identity", # use HEX colors as-is
    projection="natural earth"
)

# --- Map styling ---
fig.update_traces(
    marker_line_width=0.8,
    marker_line_color="white",
    hovertemplate="<b>%{hovertext}</b><extra></extra>"
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="#b9e6ff",
    geo=dict(
        bgcolor="#b9e6ff",
        showframe=False,
        showcoastlines=False,
        projection_scale=0.67,   # zoom out a bit
        center=dict(lat=10, lon=0),
        lataxis=dict(range=[-90, 90])
    ),
    height=650,
    dragmode=False
)

# --- Streamlit display ---
st.markdown(
    """
    <style>
    .block-container {padding:0rem; max-width:100%;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌍 Interactive World Map Dashboard")
st.write("This map is built using HEX.csv + countries.geo.json")
st.plotly_chart(fig, use_container_width=True)
