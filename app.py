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
# 2. Load Data
# -----------------------------
@st.cache_data
def load_data():
    """Loads and processes both data files."""
    try:
        # NOTE: Ensure these files are in the same directory as app.py
        df = pd.read_csv("final_with_socio_cleaned.csv")
        hex_df = pd.read_csv("Hex.csv")
    except FileNotFoundError as e:
        st.error(f"Missing required file: {e.filename}. Please place it in the same directory.")
        st.stop()
        
    df["Year"] = df["Year"].astype(int)
    df["ISO3"] = df["ISO3"].str.strip()
    df["Country"] = df["Country"].str.strip()

    hex_df["ISO3"] = hex_df["ISO3"].str.strip()
    # Create the ISO3 to Hex color mapping dictionary
    hex_map = dict(zip(hex_df["ISO3"], hex_df["hex"]))

    return df, hex_map

# Initialize global data
df, hex_map = load_data()
years = sorted(df["Year"].unique())

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

# Filter Map Data for the selected year
map_df = df[df["Year"] == year].copy()
map_df["hex"] = map_df["ISO3"].map(hex_map)

# World Map (Choropleth using Hex color mapping)
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="ISO3", # Color by ISO3 to use the discrete map
    hover_name="Country",
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
# 4. Render Map & Capture Click State
# -----------------------------
# Use a key to store the click data in st.session_state
st.plotly_chart(
    fig,
    use_container_width=True,
    key="country_map" # <-- CRITICAL FOR STABLE CLICK DETECTION
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
    country_df = df[df["ISO3"] == iso].sort_values("Year")

    if not country_df.empty:
        country_name = country_df.iloc[0]["Country"]
        st.subheader(country_name)

        # -------- KPIs --------
        latest = country_df[country_df["Year"] == year].iloc[0] # Use iloc[0] for robust single row access

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("HDI", round(latest["HDI"], 3))
        k2.metric("Life Expectancy", f"{round(latest['Life_Expectancy'], 1)} Yrs")
        k3.metric("GDP per Capita", f"${int(latest['GDP_per_capita']):,}")
        k4.metric("Median Age", f"{round(latest['Median_Age_Est'], 1)} Yrs")

        st.markdown("---")

        # -------- Historical Line Charts --------
        indicators = {
            "HDI": "HDI",
            "Life Expectancy": "Life_Expectancy",
            "GDP per Capita": "GDP_per_capita",
            "Gini Index": "Gini_Index",
            "COVID Deaths / mil": "COVID_Deaths"
        }

        cols = st.columns(2)

        for i, (label, col) in enumerate(indicators.items()):
            # Create Plotly Line Chart
            fig_line = px.line(
                country_df,
                x="Year",
                y=col,
                markers=True,
                title=label
            )
            fig_line.update_layout(
                height=300,
                template="plotly_dark", # Use consistent dark template
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
