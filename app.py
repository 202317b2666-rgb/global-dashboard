import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_float import float_init, float_box

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide"
)

float_init()

# ---------------------------------
# Load data
# ---------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    df["Year"] = df["Year"].astype(int)

    hex_df = pd.read_csv("Hex.csv")
    hex_map = dict(zip(hex_df["iso_alpha"], hex_df["hex"]))

    return df, hex_map


df, hex_map = load_data()
years = sorted(df["Year"].unique())

# ---------------------------------
# Session state
# ---------------------------------
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

# ---------------------------------
# Title
# ---------------------------------
st.markdown(
    "<h2 style='text-align:center'>🌍 Global Health Dashboard</h2>",
    unsafe_allow_html=True
)

# ---------------------------------
# Year slider (ALL YEARS)
# ---------------------------------
year = st.slider(
    "Select Year",
    min_value=min(years),
    max_value=max(years),
    value=max(years),
    step=1
)

# ---------------------------------
# World Map
# ---------------------------------
map_df = df[df["Year"] == year]

fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis",
    title=f"Global HDI Map - {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
        bgcolor="#4fa3d1"  # sea blue
    ),
    paper_bgcolor="black",
    plot_bgcolor="black"
)

selected = st.plotly_chart(fig, use_container_width=True)

# ---------------------------------
# Detect country click
# ---------------------------------
if selected and "points" in selected:
    iso = selected["points"][0]["location"]
    st.session_state.selected_country = iso
    st.session_state.show_popup = True

# ---------------------------------
# Floating Popup
# ---------------------------------
if st.session_state.show_popup and st.session_state.selected_country:

    iso = st.session_state.selected_country
    country_df = df[df["ISO3"] == iso]

    if not country_df.empty:

        with float_box(
            width="85%",
            height="90vh",
            left="7.5%",
            top="5%",
            background="#111",
            border_radius="12px",
            padding="20px",
            shadow=True,
            z_index=999
        ):

            # Header
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(
                    f"### {country_df.iloc[0]['Country']}"
                )
            with col2:
                if st.button("❌"):
                    st.session_state.show_popup = False

            st.markdown("---")

            # Indicators
            indicators = {
                "HDI": "HDI",
                "GDP per Capita": "GDP_per_capita",
                "Life Expectancy": "Life_Expectancy",
                "Median Age": "Median_Age_Est",
                "Gini Index": "Gini_Index",
                "COVID Deaths / mil": "COVID_Deaths",
                "Population Density": "Population_Density"
            }

            # Charts grid
            cols = st.columns(2)
            i = 0

            for title, col in indicators.items():
                fig_line = go.Figure()
                fig_line.add_trace(
                    go.Scatter(
                        x=country_df["Year"],
                        y=country_df[col],
                        mode="lines+markers",
                        name=title
                    )
                )
                fig_line.update_layout(
                    title=title,
                    template="plotly_dark",
                    height=300,
                    margin=dict(t=40, b=30),
                    xaxis_title="Year"
                )

                with cols[i % 2]:
                    st.plotly_chart(fig_line, use_container_width=True)

                i += 1
