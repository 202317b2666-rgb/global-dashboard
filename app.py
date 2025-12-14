import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_float import float_init

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="🌍 Global Health Dashboard",
    layout="wide"
)

float_init()

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
# Filter data by year
# -----------------------------------
year_df = df[df["Year"] == year]

# -----------------------------------
# World Map
# -----------------------------------
fig = px.choropleth(
    year_df,
    locations="ISO3",
    color="HDI",                         # 🔑 required
    hover_name="Country",
    color_continuous_scale="Viridis",
    range_color=(0.3, 0.95),
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
        oceancolor="#1f77b4",             # 🌊 sea color
        showland=True                     # ❗ no landcolor
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    clickmode="event+select"
)

# -----------------------------------
# Render map
# -----------------------------------
selected = st.plotly_chart(
    fig,
    use_container_width=True,
    key="world_map"
)

# -----------------------------------
# Floating popup container
# -----------------------------------
popup = st.container()
popup.float(
    css="""
    position: fixed;
    right: 20px;
    top: 80px;
    width: 350px;
    background-color: #111;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    z-index: 9999;
    """
)

# -----------------------------------
# Popup logic (SAFE)
# -----------------------------------
with popup:
    if selected and isinstance(selected, dict):
        if "points" in selected and len(selected["points"]) > 0:
            iso = selected["points"][0]["location"]

            country_row = year_df[year_df["ISO3"] == iso]

            if not country_row.empty:
                row = country_row.iloc[0]

                st.subheader(row["Country"])
                st.markdown(f"**Year:** {year}")
                st.markdown(f"**HDI:** {row['HDI']:.3f}")
                st.markdown(f"**Life Expectancy:** {row['Life_Expectancy']:.1f}")
                st.markdown(f"**GDP per Capita:** ${row['GDP_per_capita']:,.0f}")
        else:
            st.info("Click a country to see details")
    else:
        st.info("Click a country to see details")
