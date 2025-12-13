# app.py
import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# -----------------------------
# 1️⃣ Set Base Directory
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# 2️⃣ Load Data with Caching
# -----------------------------
@st.cache_data
def load_data():
    try:
        # CSV and GeoJSON file paths
        data_path = os.path.join(BASE_DIR, "final_with_socio_cleaned.csv")
        geojson_path = os.path.join(BASE_DIR, "countries.geo.json")
        hex_path = os.path.join(BASE_DIR, "Hex.csv")
        
        # Load data
        data = pd.read_csv(data_path)
        with open(geojson_path) as f:
            geojson = json.load(f)
        hex_df = pd.read_csv(hex_path)
        
        st.success("Data loaded successfully ✅")
        return data, geojson, hex_df
    except FileNotFoundError as e:
        st.error(f"File not found: {e.filename}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# -----------------------------
# 3️⃣ Load datasets
# -----------------------------
data, geojson, hex_df = load_data()

# -----------------------------
# 4️⃣ Sidebar
# -----------------------------
st.sidebar.title("Country Dashboard")
country_list = ["All"] + sorted(data['ISO3'].unique())
selected_country = st.sidebar.selectbox("Select Country", country_list)

# -----------------------------
# 5️⃣ Filter Data
# -----------------------------
if selected_country != "All":
    filtered_data = data[data["ISO3"] == selected_country]
else:
    filtered_data = data.copy()

# -----------------------------
# 6️⃣ Example Visualization
# -----------------------------
st.title("🌍 Global Health & Socioeconomic Dashboard")

# Example: Life Expectancy vs HDI Scatter Plot
if "LifeExpectancy" in filtered_data.columns and "HDI" in filtered_data.columns:
    fig = px.scatter(
        filtered_data,
        x="HDI",
        y="LifeExpectancy",
        color="ISO3",
        hover_name="Country",
        title="Life Expectancy vs Human Development Index"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Columns 'LifeExpectancy' or 'HDI' not found in data.")

# -----------------------------
# 7️⃣ Hex Color Mapping Example
# -----------------------------
st.subheader("Country Color Mapping (Hex) Example")
st.dataframe(hex_df.head())
