import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
# NEW IMPORT
import reverse_geocode 

# -----------------------------
# 1. Page Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide"
)

# -----------------------------
# 2. Load Data (Verified Correct)
# -----------------------------
@st.cache_data
def load_data():
    """Loads and processes both data files using the explicit column names."""
    try:
        df = pd.read_csv("final_with_socio_cleaned.csv")
        hex_df = pd.read_csv("Hex.csv")
    except FileNotFoundError as e:
        st.error(f"Missing required file: {e.filename}. Please place it in the same directory.")
        st.stop()
        
    df.columns = [col.upper() for col in df.columns] 
    df["YEAR"] = df["YEAR"].astype(int)
    df["ISO3"] = df["ISO3"].str.strip()
    df["COUNTRY"] = df["COUNTRY"].str.strip()

    hex_df = hex_df.rename(columns={
        "iso_alpha": "ISO3", 
        "hex": "HEX"         
    })
    
    hex_df["ISO3"] = hex_df["ISO3"].str.strip()
    hex_map = dict(zip(hex_df["ISO3"], hex_df["HEX"])) 
    
    return df, hex_map

# Initialize global data
df, hex_map = load_data()
years = sorted(df["YEAR"].unique())

country_list = sorted(df["COUNTRY"].unique())
country_name_to_iso = dict(zip(df["COUNTRY"], df["ISO3"]))

if 'selected_iso' not in st.session_state:
    st.session_state.selected_iso = None

# -----------------------------
# 3. Main Layout: Map & Controls
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🌍 Global Health Dashboard</h2>", unsafe_allow_html=True)

# Year Slider
year = st.slider(
    "Select Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1
)

# --- Fallback Select Box ---
selected_country_name_fallback = st.selectbox(
    "1. Select a Country for Detailed Analysis (Fallback)",
    options=[None] + country_list,
    index=0
)
if selected_country_name_fallback:
    st.session_state.selected_iso = country_name_to_iso.get(selected_country_name_fallback)


# ----------------------------------------------------
# 4. Render Folium Map & Capture Click (FINAL LOGIC)
# ----------------------------------------------------

# Create a Folium map object centered globally
m = folium.Map(location=[10, 0], zoom_start=2, tiles="cartodbdarkmatter", control_scale=True)

# Render the Folium map and capture the click event
map_data = st_folium(
    m, 
    height=500, 
    width='100%', 
    use_container_width=True,
    key="folium_map_click",
    returned_objects=["last_clicked"] 
)

# Attempt to capture the click data and perform reverse geocoding
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    
    coordinates = [(lat, lon)]
    
    try:
        # Perform reverse geocoding to get country info
        results = reverse_geocode.search(coordinates)
        
        # 'reverse-geocode' returns the two-letter country code (e.g., 'IN' for India)
        # We need the three-letter ISO3 code for filtering your DataFrame.
        # Since your DF only contains the three-letter code, we need a small helper function.
        
        country_code_2_letter = results[0]['country_code'].upper()
        
        # Simple mapping to get the full country name for lookup in your DF
        # The reverse-geocode library returns the 2-letter code.
        # We will use the full name (e.g., 'India') to find the ISO3 (e.g., 'IND').
        country_name_from_click = results[0]['country'] 
        
        # --- LOOKUP in YOUR DataFrame ---
        # Find the ISO3 code in your main data based on the country name
        clicked_iso = df[df["COUNTRY"] == country_name_from_click]["ISO3"].iloc[0]
        
        if clicked_iso:
            st.session_state.selected_iso = clicked_iso
        else:
            # Handle case where the country name isn't in your DataFrame (e.g., an ocean click)
            st.info(f"Clicked on '{country_name_from_click}', but this country is not in your data set.")
            
    except Exception as e:
        # Handle failures (e.g., clicking on water, or mapping error)
        st.warning(f"Could not resolve location: {e}")


# -----------------------------
# 5. Country Details Section (Driven by Session State)
# -----------------------------
st.markdown("---")
st.markdown("## 📊 Country Detailed Analysis")

selected_iso = st.session_state.selected_iso

if selected_iso:
    # --- This code block runs when a country is selected via the map or dropdown ---
    iso = selected_iso
    country_df = df[df["ISO3"] == iso].sort_values("YEAR")

    if not country_df.empty:
        country_name = country_df.iloc[0]["COUNTRY"]
        st.subheader(country_name)

        # -------- KPIs --------
        latest = country_df[country_df["YEAR"] == year].iloc[0] 

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("HDI", round(latest["HDI"], 3))
        k2.metric("Life Expectancy", f"{round(latest['LIFE_EXPECTANCY'], 1)} Yrs")
        k3.metric("GDP per Capita", f"${int(latest['GDP_PER_CAPITA']):,}")
        k4.metric("Median Age", f"{round(latest['MEDIAN_AGE_EST'], 1)} Yrs")

        st.markdown("---")

        # -------- Historical Line Charts --------
        indicators = {
            "HDI": "HDI",
            "Life Expectancy": "LIFE_EXPECTANCY",
            "GDP per Capita": "GDP_PER_CAPITA",
            "Gini Index": "GINI_INDEX",
            "COVID Deaths / mil": "COVID_DEATHS",
            "Population Density": "POPULATION_DENSITY"
        }

        cols = st.columns(2)

        for i, (label, col) in enumerate(indicators.items()):
            fig_line = px.line(
                country_df,
                x="YEAR",
                y=col,
                markers=True,
                title=label
            )
            fig_line.update_layout(height=300, template="plotly_dark", margin=dict(t=40, b=10, l=10, r=10))

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info(f"No detailed data available for the selected country.")
else:
    st.info("👆 Click any country on the map or use the Select Box to view detailed insights.")
