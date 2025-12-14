import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="🌍 Global Health Dashboard",
    layout="wide"
)

# -----------------------------------
# Load data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    return df

df = load_data()

# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.title("🌍 Global Health Dashboard")

year = st.sidebar.slider(
    "Select Year",
    int(df["Year"].min()),
    int(df["Year"].max()),
    int(df["Year"].max())
)

# -----------------------------------
# Filter data
# -----------------------------------
year_df = df[df["Year"] == year]

# -----------------------------------
# World Map
# -----------------------------------
fig = px.choropleth(
    year_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        showocean=True,
        oceancolor="#1f77b4"
    ),
    paper_bgcolor="black",
    plot_bgcolor="black"
)

# -----------------------------------
# Capture click events
# -----------------------------------
selected = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    override_height=600,
    key="map"
)

# -----------------------------------
# Country Details Section
# -----------------------------------
st.markdown("---")
st.subheader("📊 Country Details")

if selected:
    iso = selected[0]["location"]
    row = year_df[year_df["ISO3"] == iso]

    if not row.empty:
        row = row.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("Country", row["Country"])
        col2.metric("HDI", f"{row['HDI']:.3f}")
        col3.metric("Life Expectancy", f"{row['Life_Expectancy']:.1f}")

        col1.metric("GDP per Capita", f"${row['GDP_per_capita']:,.0f}")
        col2.metric("Median Age", f"{row['Median_Age']:.1f}")
        col3.metric("COVID Deaths / mil", f"{row['Covid_Deaths_per_million']:,.0f}")

else:
    st.info("👆 Click a country on the map to view details")
