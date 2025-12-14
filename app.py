import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Removed: from streamlit_plotly_events import plotly_events (using native events)

# -----------------------------
# Init & Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load Data (with Robustness)
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    df["Year"] = df["Year"].astype(int)
    
    # IMPORTANT FIX: Strip whitespace from key columns for reliable matching
    df["ISO3"] = df["ISO3"].str.strip()
    df["Country"] = df["Country"].str.strip()
    
    # Load Hex Data (Optional)
    try:
        hex_df = pd.read_csv("Hex.csv")
        hex_df.columns = [c.lower() for c in hex_df.columns]
        hex_df["iso_alpha"] = hex_df["iso_alpha"].str.strip() 
        hex_map = dict(zip(hex_df["iso_alpha"], hex_df["hex"]))
    except FileNotFoundError:
        st.warning("Hex.csv not found. Map colors/details may be limited.")
        hex_map = {} 

    return df, hex_map

# Global variables initialized to prevent NameError
df = None
hex_map = {}
years = [] 
country_data = None # Initialize to prevent error later

# Load the data and handle potential errors
try:
    df, hex_map = load_data()
    # Calculate years ONLY if data loading was successful
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"FATAL ERROR: Failed to load data. Ensure 'final_with_socio_cleaned.csv' exists and is correct. Details: {e}")
    df = pd.DataFrame() 
    st.stop()
    
if df.empty:
    st.warning("Data is empty after loading. Cannot display dashboard.")
    st.stop()

# -----------------------------
# Dialog Function ( The Popup )
# -----------------------------
@st.dialog("Country Overview")
def show_country_details(iso_code, data_frame):
    """
    Renders the charts inside the Streamlit dialog modal.
    data_frame is passed explicitly to use the correct filtered data.
    """
    country_data = data_frame[data_frame["ISO3"] == iso_code]
    
    if country_data.empty:
        st.warning(f"No detailed historical data available for ISO code: {iso_code}")
        return

    country_name = country_data.iloc[0]["Country"]
    st.header(country_name)

    indicators = {
        "HDI": "HDI",
        "GDP per Capita": "GDP_per_capita",
        "Life Expectancy": "Life_Expectancy",
        "Median Age": "Median_Age_Est",
        "Gini Index": "Gini_Index",
        "COVID Deaths / mil": "COVID_Deaths",
        "Population Density": "Population_Density"
    }

    cols = st.columns(2)

    for i, (title, col_name) in enumerate(indicators.items()):
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
    range_color=[0, 1], # Ensures color scale is consistent
    title=f"Global HDI Map – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        showocean=True,
        oceancolor="#0E1117",
        showland=True,
        landcolor="#1a1a1a",
        projection_type="natural earth" 
    ),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    margin=dict(t=50, b=0, l=0, r=0),
    coloraxis_colorbar=dict(title="HDI")
)

# ----------------------------------------------------
# Native Plotly Click Event & Session State
# ----------------------------------------------------

# 1. Initialize session state variable to store selected ISO code
if 'selected_iso' not in st.session_state:
    st.session_state.selected_iso = None

# 2. Define the callback function that runs on map click
def handle_map_selection():
    """
    Callback runs when the map selection changes.
    """
    # Get the data stored by the plotly_chart component with key="global_map"
    selection = st.session_state.get("global_map")
    
    if selection and selection.get("points"):
        # The location field contains the ISO3 code for choropleth maps
        clicked_iso = selection["points"][0]["location"]
        st.session_state.selected_iso = clicked_iso
        st.rerun() # Rerun to launch the dialog immediately
    else:
        st.session_state.selected_iso = None

# 3. Render the Map with the callback
st.plotly_chart(
    fig, 
    use_container_width=True, 
    on_select=handle_map_selection, # This is the action trigger
    selection_mode="points",
    key="global_map" 
)

# 4. Trigger Dialog based on Session State
if st.session_state.selected_iso:
    # Use st.dialog to show the floating popup
    show_country_details(st.session_state.selected_iso, df)
    
    # After the dialog shows, we clear the state.
    # We MUST do this only *after* the dialog has been shown on the screen.
    # The next interaction (or the dialog's close) will naturally rerun the app.
    # We clear the state here to prevent infinite dialog loop if the user clicks out of it.
    st.session_state.selected_iso = None
