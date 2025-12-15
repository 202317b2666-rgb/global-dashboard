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
# 2. Load Data (Your verified file loading logic)
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

# Get a sorted list of unique country names for the select box (as a fallback)
country_list = sorted(df["COUNTRY"].unique())

# Initialize session state for the selected ISO code
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

# --- Fallback Select Box (Hidden after debugging) ---
# Keeping the select box logic separate allows us to test the map logic exclusively
selected_country_name = st.selectbox(
    "1. Select a Country for Detailed Analysis (Fallback)",
    options=[None] + country_list,
    index=0
)
if selected_country_name:
    st.session_state.selected_iso = df[df["COUNTRY"] == selected_country_name]["ISO3"].iloc[0]


# Filter Map Data for the selected year
map_df = df[df["YEAR"] == year].copy()
map_df["HEX"] = map_df["ISO3"].map(hex_map)

# World Map (Choropleth figure creation)
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="ISO3", 
    hover_name="COUNTRY", 
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

# ----------------------------------------------------
# 4. Render Map & Capture Click State (Standard Streamlit Rerun)
# ----------------------------------------------------

click_data = st.plotly_chart(
    fig,
    use_container_width=True,
    # This is the key instruction: rerun the app on selection
    on_select="rerun", 
    selection_mode="points",
    key="map_click_event"
)

# Check for map click data AFTER the rerun
if "map_click_event" in st.session_state and st.session_state["map_click_event"] and st.session_state["map_click_event"].get("points"):
    
    # Store the clicked ISO code in the main session state variable
    clicked_iso = st.session_state["map_click_event"]["points"][0]["location"]
    st.session_state.selected_iso = clicked_iso
    
    # Reset the selection data to allow clicking the same country again
    st.session_state["map_click_event"] = None


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
        st.info(f"No detailed data available for {country_name} in year {year}.")
else:
    st.info("👆 Click any country on the map or use the Select Box to view detailed insights.")
