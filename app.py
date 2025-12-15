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
# Load Data (Important: Ensure 'final_with_socio_cleaned.csv' is present)
# -----------------------------
@st.cache_data
def load_data():
    """Loads and processes the main DataFrame."""
    try:
        # NOTE: Make sure your CSV file is in the same directory!
        df = pd.read_csv("final_with_socio_cleaned.csv")
        df["Year"] = df["Year"].astype(int)
        df["ISO3"] = df["ISO3"].str.strip()
        df["Country"] = df["Country"].str.strip()
    except FileNotFoundError:
        st.error("Error: 'final_with_socio_cleaned.csv' not found.")
        st.stop() # Stop execution if data is missing

    # Add a dummy hex_map or remove it if not needed for this version
    hex_map = {} 
    return df, hex_map

# Global Data initialization
df = pd.DataFrame()
years = [] 

try:
    df, _ = load_data()
    if df.empty:
        st.stop()
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"FATAL ERROR: Failed to process data. Details: {e}")
    st.stop()

# ----------------------------------------------------
# Chart Function: Displays charts in the main body
# ----------------------------------------------------
def display_country_charts_in_main(iso_code, data_frame, container):
    """Renders charts inside a standard container without rerunning the app."""
    
    country_data = data_frame[data_frame["ISO3"] == iso_code].sort_values(by="Year")
    
    if country_data.empty:
        container.info("No detailed historical data available.")
        return

    country_name = country_data.iloc[0]["Country"]
    container.markdown(f"## 📈 Historical Analysis for {country_name}")
    container.markdown("---")

    # Define the indicators for the time series charts
    indicators = {
        "HDI": "HDI", "GDP per Capita": "GDP_per_capita", "Life Expectancy": "Life_Expectancy", 
        "Median Age": "Median_Age_Est", "Gini Index": "Gini_Index", 
        "COVID Deaths / mil": "COVID_Deaths", "Population Density": "Population_Density"
    }

    cols = container.columns(2)

    for i, (title, col_name) in enumerate(indicators.items()):
        if col_name in country_data.columns:
            # Create a Plotly line chart
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=country_data["Year"], y=country_data[col_name], mode="lines+markers",
                line=dict(color='#00CC96', width=2), marker=dict(size=4)
            ))

            fig_line.update_layout(
                title=dict(text=title, font=dict(size=14)), template="plotly_dark", height=250,
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis=dict(title=None, showgrid=False), # Hide x-axis title/grid for cleaner look
                yaxis=dict(showgrid=True, gridcolor='#333'),
                paper_bgcolor="#0E1117", plot_bgcolor="rgba(0,0,0,0)"
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)


# -----------------------------
# Main Layout: Map & Controls
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

# Customize map appearance for dark theme
fig.update_layout(
    geo=dict(
        showframe=False, showcoastlines=True, coastlinecolor="white", 
        showocean=True, oceancolor="#0E1117", # Set ocean color to match dark background
        showland=True, landcolor="#1a1a1a", projection_type="natural earth" 
    ),
    paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", 
    margin=dict(t=50, b=0, l=0, r=0), 
    coloraxis_colorbar=dict(title="HDI")
)

# ----------------------------------------------------
# Render Map and Detect Click State
# ----------------------------------------------------

# Render the map and store the selection data in st.session_state["global_map"]
st.plotly_chart(
    fig, 
    use_container_width=True, 
    key="global_map" 
)

# Get the selection data directly from the session state
selection = st.session_state.get("global_map")
selected_iso = None

# Extract the ISO code from the map click event
if selection and selection.get("points"):
    selected_iso = selection["points"][0]["location"]


# ----------------------------------------------------
# Display Permanent Chart Section
# ----------------------------------------------------
st.markdown("---")
st.markdown("## Detailed Country Analysis", unsafe_allow_html=True)

# Create a dedicated container for the historical charts
chart_container = st.container()

if selected_iso:
    # If a country is selected, display the charts inside the container
    display_country_charts_in_main(selected_iso, df, chart_container)
else:
    # If nothing is selected, display a helpful prompt
    chart_container.info("Click a country on the map above to view its historical health and economic data.")
