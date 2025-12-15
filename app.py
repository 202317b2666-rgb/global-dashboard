import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 1. Page Config
# -----------------------------
st.set_page_config(
    page_title="Sample Dashboard",
    layout="wide"
)

# -----------------------------
# 2. Sample Data Creation (Replaces load_data)
# -----------------------------
# Create sample data that mimics the structure of your files
def create_sample_data():
    data = {
        'COUNTRY': ['USA', 'USA', 'USA', 'CAN', 'CAN', 'CAN', 'FRA', 'FRA', 'FRA'],
        'ISO3': ['USA', 'USA', 'USA', 'CAN', 'CAN', 'CAN', 'FRA', 'FRA', 'FRA'],
        'YEAR': [2022, 2023, 2024, 2022, 2023, 2024, 2022, 2023, 2024],
        'GDP_PER_CAPITA': [70000, 72000, 74000, 50000, 51000, 52000, 45000, 46000, 47000],
        'HDI': [0.92, 0.93, 0.94, 0.91, 0.92, 0.93, 0.90, 0.91, 0.92],
        'LIFE_EXPECTANCY': [78.5, 78.8, 79.1, 81.0, 81.3, 81.6, 82.0, 82.3, 82.6],
        'MEDIAN_AGE_EST': [38.5, 39.0, 39.5, 41.0, 41.5, 42.0, 42.5, 43.0, 43.5],
        'COVID_DEATHS': [1500, 100, 50, 1200, 80, 40, 900, 60, 30],
        'GINI_INDEX': [48.0, 48.1, 48.2, 33.0, 33.1, 33.2, 32.0, 32.1, 32.2],
        'POPULATION_DENSITY': [35.0, 36.0, 37.0, 4.0, 4.1, 4.2, 120.0, 121.0, 122.0]
    }
    df_sample = pd.DataFrame(data)
    return df_sample

# Load the sample data
df = create_sample_data()
years = sorted(df["YEAR"].unique())
country_list = sorted(df["COUNTRY"].unique())


# -----------------------------
# 3. Main Layout: Map & Controls
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🌍 Global Health Dashboard (Sample Data)</h2>", unsafe_allow_html=True)

# Year Slider
year = st.slider(
    "Select Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1
)

# --- NEW INTERACTION: Select Box ---
selected_country_name = st.selectbox(
    "1. Select a Country for Detailed Analysis",
    options=[None] + country_list, 
    index=0
)

# Determine the ISO code for filtering
selected_iso = df[df["COUNTRY"] == selected_country_name]["ISO3"].iloc[0] if selected_country_name else None

# Filter Map Data for the selected year
map_df = df[df["YEAR"] == year].copy()

# World Map (Basic Choropleth)
# We use one of Plotly's built-in datasets for the map data (lifeExp) to guarantee the map loads
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="HDI", # We use HDI for coloring instead of hex codes for simplicity
    hover_name="COUNTRY",
    color_continuous_scale=px.colors.sequential.Plasma,
    title=f"Sample Global Overview – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        showland=True,
        projection_type="natural earth"
    ),
    margin=dict(t=50, b=0, l=0, r=0),
)

# Render the Map
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 4. Country Details Section (Driven by Select Box)
# -----------------------------
st.markdown("---")
st.markdown("## 📊 Country Detailed Analysis")

if selected_iso:
    # --- This code block will run when a country is selected ---
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
            "Median Age": "MEDIAN_AGE_EST"
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
        st.info(f"No detailed data available for {selected_country_name}.")
else:
    st.info("👆 Use the Select Box above to view detailed insights.")
