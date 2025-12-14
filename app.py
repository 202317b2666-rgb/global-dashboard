import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# -----------------------------
# Init & Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    # Load Main Data
    df = pd.read_csv("final_with_socio_cleaned.csv")
    df["Year"] = df["Year"].astype(int)

    # Load Hex Data (Optional: kept based on your previous code)
    try:
        hex_df = pd.read_csv("Hex.csv")
        hex_df.columns = [c.lower() for c in hex_df.columns]
        hex_map = dict(zip(hex_df["iso_alpha"], hex_df["hex"]))
    except FileNotFoundError:
        hex_map = {} # Fallback if file missing

    return df, hex_map

# Load the data
try:
    df, hex_map = load_data()
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -----------------------------
# Dialog Function ( The Popup )
# -----------------------------
@st.dialog("Country Overview")
def show_country_details(iso_code):
    """
    This function renders the popup modal.
    It runs inside a separate container on top of the map.
    """
    country_data = df[df["ISO3"] == iso_code]
    
    if country_data.empty:
        st.warning("No detailed data available for this country.")
        return

    country_name = country_data.iloc[0]["Country"]
    st.header(country_name)

    # Define the charts you want to show
    indicators = {
        "HDI": "HDI",
        "GDP per Capita": "GDP_per_capita",
        "Life Expectancy": "Life_Expectancy",
        "Median Age": "Median_Age_Est",
        "Gini Index": "Gini_Index",
        "COVID Deaths / mil": "COVID_Deaths",
        "Population Density": "Population_Density"
    }

    # Create a grid layout for charts
    cols = st.columns(2)

    for i, (title, col_name) in enumerate(indicators.items()):
        # Only plot if column exists in CSV
        if col_name in country_data.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=country_data["Year"],
                y=country_data[col_name],
                mode="lines+markers",
                line=dict(color='#00CC96', width=2),
                marker=dict(size=4)
            ))

            fig_line.update_layout(
                title=dict(text=title, font=dict(size=14)),
                template="plotly_dark",
                height=200,
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis=dict(title=None, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#333'),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# Main Layout
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

# Filter Data for Map
map_df = df[df["Year"] == year]

# Create Map
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis",
    range_color=[0, 1], # Fixes scale stability across years
    title=f"Global HDI Map – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        showocean=True,
        oceancolor="#0E1117",  # Matches Streamlit dark theme better
        showland=True,
        landcolor="#1a1a1a",
        projection_type="natural earth" 
    ),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    margin=dict(t=50, b=0, l=0, r=0),
    coloraxis_colorbar=dict(title="HDI")
)

# -----------------------------
# Render Map & Capture Click
# -----------------------------
# We use a container to keep the layout tight
with st.container():
    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=600,
        override_width="100%"
    )

# -----------------------------
# Trigger Popup
# -----------------------------
if selected_points:
    # Extract the ISO code from the clicked point
    clicked_iso = selected_points[0].get("location", None) # Safe get
    
    if clicked_iso:
        show_country_details(clicked_iso)
