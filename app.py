import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_float import float_init # <-- New import

# -----------------------------
# Init & Config
# -----------------------------
float_init() # <-- Initialize float component

st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load Data (Robustness kept)
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    df["Year"] = df["Year"].astype(int)
    df["ISO3"] = df["ISO3"].str.strip()
    df["Country"] = df["Country"].str.strip()
    
    try:
        hex_df = pd.read_csv("Hex.csv")
        hex_df.columns = [c.lower() for c in hex_df.columns]
        hex_df["iso_alpha"] = hex_df["iso_alpha"].str.strip() 
        hex_map = dict(zip(hex_df["iso_alpha"], hex_df["hex"]))
    except FileNotFoundError:
        hex_map = {} 

    return df, hex_map

# Initialize variables
df = None
years = [] 

try:
    df, hex_map = load_data()
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"FATAL ERROR: Failed to load data. Details: {e}")
    df = pd.DataFrame() 
    st.stop()
    
if df.empty:
    st.warning("Data is empty after loading. Cannot display dashboard.")
    st.stop()

# ----------------------------------------------------
# Floating Popup Container Function (THE FIX)
# ----------------------------------------------------
def show_floating_popup(iso_code, data_frame):
    """Renders the detailed charts inside a manually floating container."""
    
    # 1. Setup the floating container
    popup = st.container()
    popup.float(
        # Position the popup centrally and make it large
        css="position:fixed; top:5%; left:5%; width:90%; height:90%; z-index:99999; background-color:#111; border-radius:12px; overflow-y:auto; padding:20px; box-shadow: 0 0 20px rgba(0,0,0,0.8);"
    )

    with popup:
        # 2. Get data and title
        country_data = data_frame[data_frame["ISO3"] == iso_code]
        if country_data.empty:
            st.warning(f"No detailed historical data available for ISO code: {iso_code}")
            return
            
        country_name = country_data.iloc[0]["Country"]
        
        # 3. Header and Close Button
        col_head, col_close = st.columns([9, 1])
        with col_head:
            st.markdown(f"<h2 style='text-align:center; color:white;'>{country_name}</h2>", unsafe_allow_html=True)
        with col_close:
            # IMPORTANT: Button to clear the state and force rerun
            if st.button("❌", key="close_float_btn"):
                st.session_state.selected_iso = None
                st.rerun() # Force a full refresh to hide the popup

        # 4. Chart Logic
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
                    title=dict(text=title, font=dict(size=14)), template="plotly_dark", height=200,
                    margin=dict(t=30, b=10, l=10, r=10),
                    xaxis=dict(title=None, showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'),
                    paper_bgcolor="#111", plot_bgcolor="#111" # Use a solid background for contrast
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

# Filter Data and Create Map (Same as before)
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
# Native Plotly Click Event & Session State
# ----------------------------------------------------

if 'selected_iso' not in st.session_state:
    st.session_state.selected_iso = None

def handle_map_selection():
    selection = st.session_state.get("global_map")
    
    if selection and selection.get("points"):
        clicked_iso = selection["points"][0]["location"]
        st.session_state.selected_iso = clicked_iso
        st.rerun() 
    else:
        st.session_state.selected_iso = None

# Render the Map with the callback
st.plotly_chart(
    fig, 
    use_container_width=True, 
    on_select=handle_map_selection, 
    selection_mode="points",
    key="global_map" 
)

# ----------------------------------------------------
# Trigger Floating Popup (THE NEW LOGIC)
# ----------------------------------------------------
if st.session_state.selected_iso:
    show_floating_popup(st.session_state.selected_iso, df)
