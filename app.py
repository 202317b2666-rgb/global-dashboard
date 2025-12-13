# Step 0: Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Step 1: Load datasets
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    with open("countries.geo.json") as f:
        geojson = json.load(f)
    hex_df = pd.read_csv("Hex.csv")
    return df, geojson, hex_df

data, geojson, hex_df = load_data()

# Step 2: Page title
st.set_page_config(page_title="Global Health Dashboard", layout="wide")
st.title("🌍 Global Health & Socio-Economic Dashboard")

# Step 3: Country selection
countries = ["All"] + sorted(data['iso_alpha'].unique())
selected_country = st.selectbox("Select a Country", countries)

# Step 4: Filter data
if selected_country != "All":
    filtered_data = data[data['iso_alpha'] == selected_country]
else:
    filtered_data = data

# Step 5: Display dataframe
st.subheader("Data Preview")
st.dataframe(filtered_data.head(20))

# Step 6: Example Plot
st.subheader("Life Expectancy vs HDI")
fig = px.scatter(
    filtered_data,
    x="HDI",
    y="LEx",
    color="iso_alpha",
    hover_data=["iso_alpha", "year"],
    title="Life Expectancy vs HDI"
)
st.plotly_chart(fig, use_container_width=True)
