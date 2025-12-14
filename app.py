import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Init & Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load Data (Robustness Kept)
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_with_socio_cleaned.csv")
        df["Year"] = df["Year"].astype(int)
        df["ISO3"] = df["ISO3"].str.strip()
        df["Country"] = df["Country"].str.strip()
    except FileNotFoundError:
        st.error("Error: 'final_with_socio_cleaned.csv' not found.")
        return pd.DataFrame(), {}
    
    try:
        hex_df = pd.read_csv("Hex.csv")
        hex_df.columns = [c.lower() for c in hex_df.columns]
        hex_map = dict(zip(hex_df["iso_alpha"].str.strip(), hex_df["hex"]))
    except FileNotFoundError:
        hex_map = {} 

    return df, hex_map

# Initialize variables
df = None
years = [] 

try:
    df, hex_map = load_data()
    if df.empty:
        st.stop()
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"FATAL ERROR: Failed to process data. Details: {e}")
    st.stop()

# ----------------------------------------------------
# Chart Function: Displays charts inside the Expander
# ----------------------------------------------------
def display_country_charts(iso_code, data_frame):
    """Renders charts inside the dedicated Expander container."""
    
    country_data = data_frame[data_frame["ISO3"] == iso_code]
    
    if country_data.empty:
        st.warning("No detailed historical data available.")
        return

    # 1. Chart Logic
    indicators = {
        "HDI": "HDI", "GDP per Capita": "GDP_per_capita", "Life Expectancy": "Life_Expectancy", 
        "Median Age": "Median_Age_Est", "Gini Index": "Gini_Index", 
        "COVID Deaths / mil": "COVID_Deaths", "Population Density": "Population_Density"
    }

    cols = st.columns(2)

    for i, (title, col_name) in enumerate(indicators.items()):
        if col_name in country_data.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=country_data["Year"], y=country_data[col_name], mode="lines+markers",
                line=dict(color='#00CC96', width=2), marker=dict(size=4)
            ))

            fig_line.update_layout(
                title=dict(text=title, font=dict(size=14)), template="plotly_dark", height=250,
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis=dict(title=None), yaxis=dict(showgrid=True, gridcolor='#333'),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)


# -----------------------------
# Main Layout
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🌍 Global Health Dashboard</h2>", unsafe_allow_html=True)

# Year Slider
year = st.slider(
    "Select Year", min_value=int(min(years)), max_value=int(max(years)), value=int(max(years)), step=1
)

# Filter Data and Create Map
map_df = df[df["Year"] == year]

fig = px.choropleth(
    map_df, locations="ISO3", color="HDI", hover_name="Country", color_continuous_scale="Viridis",
    range_color=[0, 1], title=f"Global HDI Map – {year}"
)

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, coastlinecolor="white", showocean=True, oceancolor="#0E1117", 
             showland=True, landcolor="#1a1a1a", projection_type="natural earth" ),
    paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", margin=dict(t=50, b=0, l=0, r=0), coloraxis_colorbar=dict(title="HDI")
)

# ----------------------------------------------------
# Click Detection & Expander Management (THE RELIABLE FIX)
# ----------------------------------------------------

if 'selected_iso' not in st.session_state:
    st.session_state.selected_iso = None

def set_selected_country():
    """Reads the latest selection from the map and updates the state."""
    selection = st.session_state.get("global_map")
    
    if selection and selection.get("points"):
        clicked_iso = selection["points"][0]["location"]
        st.session_state.selected_iso = clicked_iso
    else:
        # User clicked on the ocean/unmapped area
        st.session_state.selected_iso = None
    
# Render the Map with the state update function
st.plotly_chart(
    fig, 
    use_container_width=True, 
    on_select=set_selected_country, # State is updated here
    selection_mode="points",
    key="global_map" 
)

# ----------------------------------------------------
# Display Charts in an Expander Below the Map
# ----------------------------------------------------

# If a country is selected, find its name for the expander title
country_name_for_expander = "Historical Data"
is_expander_open = False

if st.session_state.selected_iso:
    # Use the selected ISO to get the country name
    selected_country_data = df[df["ISO3"] == st.session_state.selected_iso]
    if not selected_country_data.empty:
        country_name = selected_country_data.iloc[0]["Country"]
        country_name_for_expander = f"📊 Historical Analysis for {country_name}"
        is_expander_open = True # Open the expander when a country is selected

# Create the Expander
with st.expander(country_name_for_expander, expanded=is_expander_open):
    if st.session_state.selected_iso:
        # Display the charts inside the open expander
        display_country_charts(st.session_state.selected_iso, df)
    else:
        st.info("Click a country on the map above to view its historical health and economic data.")
