import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_float import float_init

# -----------------------------
# Init floating support
# -----------------------------
float_init()

st.set_page_config(
    page_title="Global Health Dashboard",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    df["Year"] = df["Year"].astype(int)

    hex_df = pd.read_csv("Hex.csv")

    # normalize column names
    hex_df.columns = [c.lower() for c in hex_df.columns]

    hex_map = dict(zip(hex_df["iso_alpha"], hex_df["hex"]))

    return df, hex_map


df, hex_map = load_data()
years = sorted(df["Year"].unique())

# -----------------------------
# Header
# -----------------------------
st.markdown(
    "<h2 style='text-align:center;'>🌍 Global Health Dashboard</h2>",
    unsafe_allow_html=True
)

# -----------------------------
# Year Slider (ALL YEARS)
# -----------------------------
year = st.slider(
    "Select Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1
)

# -----------------------------
# Map Data
# -----------------------------
map_df = df[df["Year"] == year].copy()
map_df["color"] = map_df["ISO3"].map(hex_map)

# -----------------------------
# World Map
# -----------------------------
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis",
    title=f"Global HDI Map – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
        bgcolor="#1f77b4"  # sea blue
    ),
    paper_bgcolor="black",
    plot_bgcolor="black"
)

selected = st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Popup State
# -----------------------------
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

# -----------------------------
# Handle Click
# -----------------------------
if selected and isinstance(selected, dict):
    if "points" in selected:
        st.session_state.selected_country = selected["points"][0]["location"]

# -----------------------------
# Floating Popup
# -----------------------------
if st.session_state.selected_country:

    iso = st.session_state.selected_country
    country_df = df[df["ISO3"] == iso]

    country_name = country_df.iloc[0]["Country"]

    popup = st.container()
    popup.float(
        top="5%",
        left="50%",
        transform="translateX(-50%)",
        width="90%",
        height="90%",
        z_index=999,
        background="#111",
        border_radius="10px",
        padding="20px"
    )

    with popup:
        st.markdown(
            f"<h3 style='text-align:center;'>{country_name}</h3>",
            unsafe_allow_html=True
        )

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

        i = 0
        for title, col in indicators.items():
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=country_df["Year"],
                y=country_df[col],
                mode="lines+markers"
            ))

            fig_line.update_layout(
                title=title,
                template="plotly_dark",
                height=250,
                margin=dict(t=40, b=20),
                xaxis=dict(title="Year", nticks=8)
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)

            i += 1

        if st.button("❌ Close"):
            st.session_state.selected_country = None
