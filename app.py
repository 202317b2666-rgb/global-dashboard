import streamlit as st
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(__file__)

def load_data():
    # Check if files exist
    for file in ["final_with_socio_cleaned.csv", "countries.geo.json", "Hex.csv"]:
        path = os.path.join(BASE_DIR, file)
        if not os.path.exists(path):
            st.error(f"File not found: {path}")
            st.stop()  # Stop the app if file is missing

    df = pd.read_csv(os.path.join(BASE_DIR, "final_with_socio_cleaned.csv"))
    
    with open(os.path.join(BASE_DIR, "countries.geo.json")) as f:
        geojson = json.load(f)
    
    hex_df = pd.read_csv(os.path.join(BASE_DIR, "Hex.csv"))
    
    return df, geojson, hex_df

data, geojson, hex_df = load_data()
st.write("Data loaded successfully ✅")
