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
# 2. Load Data (Verified Correct)
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

# Get a sorted list of unique country names for the search box
country_list = sorted(df["COUNTRY"].unique())
country_to_iso = dict(zip(df["COUNTRY"], df["ISO3"]))

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

# ----------------------------------------------------
# NEW INTERACTION LOGIC: Country Search Box
# ----------------------------------------------------
selected_country_name = st.selectbox(
    "Search or Select a Country for Detailed Analysis",
    options=[None] + country_list, # Add None as the initial state
    index=0
)

# Determine the ISO code based on the selection
if selected_country_name:
    selected_iso = country_to_iso.get(selected_country_name)
else:
    selected_iso = None

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

# Optional: Highlight selected country on the map
if selected_iso:
    # Add a separate trace for the selected country to highlight it
    selected_country_data = map_df[map_df["ISO3"] == selected_iso]
    if not selected_country_data.empty:
        fig.add_trace(
            go.Choropleth(
                locations=selected_country_data["ISO3"],
                z=[1] * len(selected_country_data), # Dummy data for visibility
                showscale=False,
                marker_line_color='white',
                marker_line_width=3,
                hoverinfo='none',
                name=selected_country_name
            )
        )


# Customize map appearance for dark theme (kept for consistent style)
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

# Render the Map
st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# 4. Country Details Section (Driven by Select Box)
# -----------------------------
st.markdown("---")
st.markdown("## 📊 Country Detailed Analysis")

if selected_iso:
    # The ISO code is correctly derived from the select box
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
        st.info(f"No detailed data available for {selected_country_name}.")
else:
    st.info("👆 Use the Search/Select box above to view detailed insights.")
