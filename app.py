import streamlit as st
import pandas as pd
import plotly.express as px

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
    plot_bgcolor="black",
    clickmode="event+select"
)

# -----------------------------------
# Render Map
# -----------------------------------
selected = st.plotly_chart(
    fig,
    use_container_width=True,
    key="world_map"
)

# -----------------------------------
# Country selection logic
# -----------------------------------
selected_country = None

if selected and isinstance(selected, dict):
    if "points" in selected and len(selected["points"]) > 0:
        selected_country = selected["points"][0]["location"]

# -----------------------------------
# Popover (Stable Solution)
# -----------------------------------
with st.popover("📊 Country Details", use_container_width=True):
    if selected_country:
        row = year_df[year_df["ISO3"] == selected_country]

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
        st.info("Click a country on the map to view details")
