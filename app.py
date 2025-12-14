import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Removed: from streamlit_plotly_events import plotly_events

# -----------------------------
# Init & Config
# -----------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load Data (with Cleaning)
# -----------------------------
@st.cache_data
def load_data():
    # Load Main Data
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
        hex_map = {} 

    return df, hex_map

# Load the data and handle potential errors
try:
    df, hex_map = load_data()
    years = sorted(df["Year"].unique())
except Exception as e:
    st.error(f"Error loading data. Please check 'final_with_socio_cleaned.csv': {e}")
    st.stop()

# -----------------------------
# Dialog Function ( The Popup )
# -----------------------------
# Note: st.dialog is used, but triggered by st.query_params, not session_state
@st.dialog("Country Overview")
def show_country_details(iso_code):
    """
    Renders the charts inside the Streamlit dialog modal.
    """
    country_data = df[df["ISO3"] == iso_code]
    
    if country_data.empty:
        st.warning("No detailed data available for this country.")
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
    range_color=[0, 1],
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

# -----------------------------
# Use Native Plotly Click Event (The FIX)
# -----------------------------
# By giving the chart a key, Streamlit captures click events automatically
st.plotly_chart(
    fig, 
    use_container_width=True, 
    on_select="rerun", # Rerun the app when a point is selected
    selection_mode="points", # We want to select points (countries)
    key="global_map"
)

# -----------------------------
# Trigger Dialog using Query Parameters (The FIX)
# -----------------------------
# The selection data is stored in st.session_state["global_map"]
selection = st.session_state.get("global_map")

# Check if points were selected
if selection and selection.get("points"):
    # The customdata field holds the underlying data we want (ISO3 in this case)
    # For choropleth, the location in the data is the ISO3 code
    clicked_iso = selection["points"][0]["location"]
    
    # Store the clicked ISO in the URL query parameters
    st.query_params["selected_country"] = clicked_iso
    st.query_params["open_dialog"] = "true" 
    st.rerun()

# -----------------------------
# Show Dialog
# -----------------------------
# The page reloads (reruns) and checks the URL parameters
if st.query_params.get("open_dialog") == "true":
    iso_code = st.query_params.get("selected_country")
    if iso_code:
        show_country_details(iso_code)
    
    # After the dialog is closed by its internal 'X' button, 
    # it clears the query params so it doesn't immediately reappear on the next run
    st.query_params.pop("selected_country", None)
    st.query_params.pop("open_dialog", None)
