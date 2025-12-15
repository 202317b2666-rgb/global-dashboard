import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# 1. Page Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide"
)

# -----------------------------
# 2. Load Data (Corrected for column names and case)
# -----------------------------
@st.cache_data
def load_data():
    """Loads and processes both data files using the explicit column names."""
    try:
        # Load dataframes
        df = pd.read_csv("final_with_socio_cleaned.csv")
        hex_df = pd.read_csv("Hex.csv")
    except FileNotFoundError as e:
        # Display a clear error if files are missing
        st.error(f"Missing required file: {e.filename}. Please place it in the same directory.")
        st.stop()
        
    # --- Standardize and Clean final_with_socio_cleaned.csv (df) ---
    # Convert all columns to uppercase for consistent access (e.g., 'Year' -> 'YEAR')
    df.columns = [col.upper() for col in df.columns] 
    
    # Cleaning/Type Conversion
    df["YEAR"] = df["YEAR"].astype(int)
    df["ISO3"] = df["ISO3"].str.strip()
    df["COUNTRY"] = df["COUNTRY"].str.strip()

    # --- Standardize and Clean Hex.csv (hex_df) ---
    # Rename the specific columns based on your provided headers
    hex_df = hex_df.rename(columns={
        "iso_alpha": "ISO3", # Rename 'iso_alpha' to 'ISO3'
        "hex": "HEX"         # Rename 'hex' to 'HEX'
    })
    
    # Strip whitespace from the code column
    hex_df["ISO3"] = hex_df["ISO3"].str.strip()
    
    # Create the ISO3 to HEX color mapping dictionary
    hex_map = dict(zip(hex_df["ISO3"], hex_df["HEX"])) 
    
    return df, hex_map

# Initialize global data
df, hex_map = load_data()
# Use the corrected uppercase column name 'YEAR'
years = sorted(df["YEAR"].unique())

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

# Filter Map Data for the selected year (Use 'YEAR')
map_df = df[df["YEAR"] == year].copy()
map_df["HEX"] = map_df["ISO3"].map(hex_map)

# World Map (Choropleth using Hex color mapping)
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="ISO3", 
    hover_name="COUNTRY", # Use 'COUNTRY'
    color_discrete_map=hex_map,
    title=f"Global Health Overview – {year}"
)

# Customize map appearance for dark theme
fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        showocean=True, oceancolor="#0E1117", 
        showland=True, landcolor="#1a1a1a",
        projection_type="natural earth"
    ),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    margin=dict(t=50, b=0, l=0, r=0),
    showlegend=False
)

# -----------------------------
# 4. Render Map & Capture Click State (Stable Method)
# -----------------------------
# Use a key to store the click data in st.session_state
st.plotly_chart(
    fig,
    use_container_width=True,
    key="country_map" 
)

# -----------------------------
# 5. Country Details Section
# -----------------------------
st.markdown("---")
st.markdown("## 📊 Country Detailed Analysis")

# Check session state for map click data
click_data = st.session_state.get("country_map")

if click_data and click_data.get("points"):
    # Extract the ISO code of the clicked country
    iso = click_data["points"][0]["location"]
    # Use 'YEAR' for sorting
    country_df = df[df["ISO3"] == iso].sort_values("YEAR")

    if not country_df.empty:
        # Use 'COUNTRY'
        country_name = country_df.iloc[0]["COUNTRY"]
        st.subheader(country_name)

        # -------- KPIs --------
        # Use 'YEAR'
        latest = country_df[country_df["YEAR"] == year].iloc[0] 

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("HDI", round(latest["HDI"], 3)) # Use 'HDI'
        k2.metric("Life Expectancy", f"{round(latest['LIFE_EXPECTANCY'], 1)} Yrs") # Use 'LIFE_EXPECTANCY'
        k3.metric("GDP per Capita", f"${int(latest['GDP_PER_CAPITA']):,}") # Use 'GDP_PER_CAPITA'
        k4.metric("Median Age", f"{round(latest['MEDIAN_AGE_EST'], 1)} Yrs") # Use 'MEDIAN_AGE_EST'

        st.markdown("---")

        # -------- Historical Line Charts --------
        indicators = {
            "HDI": "HDI",
            "Life Expectancy": "LIFE_EXPECTANCY", # Corrected key
            "GDP per Capita": "GDP_PER_CAPITA",   # Corrected key
            "Gini Index": "GINI_INDEX",           # Corrected key
            "COVID Deaths / mil": "COVID_DEATHS",  # Corrected key
            "Population Density": "POPULATION_DENSITY" # Added another one for completeness
        }

        cols = st.columns(2)

        for i, (label, col) in enumerate(indicators.items()):
            # Create Plotly Line Chart
            fig_line = px.line(
                country_df,
                x="YEAR", # Use 'YEAR'
                y=col,
                markers=True,
                title=label
            )
            fig_line.update_layout(
                height=300,
                template="plotly_dark",
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                margin=dict(t=40, b=10, l=10, r=10)
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("No detailed data available for the selected country.")
else:
    st.info("👆 Click any country on the map above to view detailed insights.")
