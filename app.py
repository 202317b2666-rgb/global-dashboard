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
    hex_df = pd.read_csv("Hex.csv")
    return df, hex_df

df, hex_df = load_data()

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
# Filter year
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
    color_continuous_scale="Viridis",
    range_color=(0.3, 0.95)
)

fig.update_traces(
    marker_line_width=0.5,
    marker_line_color="white"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        showocean=True,
        oceancolor="#1f77b4",
        showland=True
    ),
    paper_bgcolor="black",
    plot_bgcolor="black"
)

# -----------------------------------
# Capture click events (THIS IS THE FIX)
# -----------------------------------
selected_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=600,
    key="map"
)

# -----------------------------------
# POPUP (Popover)
# -----------------------------------
with st.popover("📊 Country Details", use_container_width=True):
    if selected_points:
        iso = selected_points[0]["location"]
        row = year_df[year_df["ISO3"] == iso]

        if not row.empty:
            row = row.iloc[0]

            st.subheader(row["Country"])
            st.markdown(f"**Year:** {year}")

            st.metric("HDI", f"{row['HDI']:.3f}")
            st.metric("Life Expectancy", f"{row['Life_Expectancy']:.1f}")
            st.metric("GDP per Capita", f"${row['GDP_per_capita']:,.0f}")
            st.metric("Median Age", f"{row['Median_Age']:.1f}")
            st.metric("COVID Deaths / mil", f"{row['Covid_Deaths_per_million']:,.0f}")
    else:
        st.info("👆 Click a country on the map")
