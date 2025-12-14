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
# Load Data (Kept Robust)
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
# Popup Function: Guaranteed Full-Screen Overlay (THE FIX)
# ----------------------------------------------------
def show_overlay_popup(iso_code, data_frame, placeholder):
    """Renders charts in a guaranteed full-screen container that overlays the entire app."""
    
    # Use the provided placeholder to insert the overlay content
    with placeholder.container():
        # Apply CSS for full-screen overlay (High Z-index, fixed position)
        st.markdown(
            f"""
            <style>
            .full-screen-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(14, 17, 23, 0.95); /* Semi-transparent dark background */
                z-index: 10000; /* Extremely high z-index to ensure it sits on top */
                overflow-y: auto;
                padding: 40px;
                box-shadow: 0 0 50px rgba(0, 0, 0, 0.9);
            }}
            .stButton>button {{
                width: 100%; /* Make the close button easy to click */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Start the overlay content container
        with st.container():
            st.markdown('<div class="full-screen-overlay">', unsafe_allow_html=True)
            
            # 1. Get data
            country_data = data_frame[data_frame["ISO3"] == iso_code]
            country_name = country_data.iloc[0]["Country"]
            
            # 2. Header and Close Button
            col_head, col_close = st.columns([8, 2])
            with col_head:
                st.markdown(f"<h1 style='text-align:center; color:white; margin-top:0;'>{country_name}</h1>", unsafe_allow_html=True)
            with col_close:
                # IMPORTANT: Button to clear the state and force rerun
                if st.button("❌ CLOSE ANALYSIS", key="close_overlay_btn"):
                    st.session_state.selected_iso = None
                    st.rerun() 

            st.markdown("---")
            
            # 3. Chart Logic (Same as before)
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
                        xaxis=dict(title=None, showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                    )

                    with cols[i % 2]:
                        st.plotly_chart(fig_line, use_container_width=True)
                        
            st.markdown("</div>", unsafe_allow_html=True)


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
# Click Detection & Overlay Management
# ----------------------------------------------------

# Placeholder setup: This is critical for controlling the overlay
overlay_placeholder = st.empty() 

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
# Trigger the Overlay
# ----------------------------------------------------
if st.session_state.selected_iso:
    # Pass the placeholder to the function so it knows where to draw the overlay
    show_overlay_popup(st.session_state.selected_iso, df, overlay_placeholder)
