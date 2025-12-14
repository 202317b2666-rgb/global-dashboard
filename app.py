import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_float import float_init, float_css

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="🌍 Global Health Dashboard",
    layout="wide"
)

float_init()

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
# Year Slider
# -----------------------------
year = st.slider(
    "Select Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1
)

# -----------------------------
# World Map
# -----------------------------
dff = df[df["Year"] == year]

fig = px.choropleth(
    dff,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
        bgcolor="#4da6ff"  # sea blue
    ),
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    margin=dict(l=0, r=0, t=30, b=0)
)

selected = st.plotly_chart(
    fig,
    use_container_width=True,
    on_select="rerun"
)

# -----------------------------
# Floating Popup Container
# -----------------------------
popup_container = st.container()
popup_container.float(float_css(
    position="fixed",
    top="5%",
    left="50%",
    transform="translateX(-50%)",
    width="85%",
    height="90%",
    background="#111",
    padding="20px",
    border_radius="10px",
    z_index="999",
    overflow_y="auto"
))

# -----------------------------
# Handle Selection (SAFE)
# -----------------------------
if isinstance(selected, dict) and "points" in selected and len(selected["points"]) > 0:

    iso = selected["points"][0].get("location")

    if iso:
        country_df = df[df["ISO3"] == iso]

        if not country_df.empty:
            country_name = country_df.iloc[0]["Country"]

            with popup_container:
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
                        mode="lines+markers",
                        name=title
                    ))

                    fig_line.update_layout(
                        title=title,
                        template="plotly_dark",
                        height=300,
                        margin=dict(t=40, b=30),
                        xaxis=dict(
                            title="Year",
                            tickmode="linear",
                            dtick=5
                        )
                    )

                    with cols[i % 2]:
                        st.plotly_chart(fig_line, use_container_width=True)

                    i += 1
