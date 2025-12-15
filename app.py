import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
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
    hex_df = pd.read_csv("Hex.csv")

    # ---- Clean main dataset ----
    df["Year"] = df["Year"].astype(int)
    df["ISO3"] = df["ISO3"].str.strip()
    df["Country"] = df["Country"].str.strip()

    # ---- Clean HEX dataset ----
    hex_df.columns = hex_df.columns.str.lower().str.strip()
    hex_df.rename(columns={"iso_alpha": "ISO3"}, inplace=True)
    hex_df["ISO3"] = hex_df["ISO3"].str.strip()

    hex_map = dict(zip(hex_df["ISO3"], hex_df["hex"]))

    return df, hex_map

df, hex_map = load_data()
years = sorted(df["Year"].unique())

# -----------------------------
# Title
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🌍 Global Health Dashboard</h2>", unsafe_allow_html=True)

# -----------------------------
# Controls (MAIN PAGE)
# -----------------------------
c1, c2 = st.columns([2, 1])

with c1:
    year = st.slider(
        "Select Year",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=int(max(years))
    )

with c2:
    country_list = sorted(df["Country"].unique())
    selected_country = st.selectbox(
        "Select Country",
        country_list
    )

# -----------------------------
# Map Data
# -----------------------------
map_df = df[df["Year"] == year].copy()

# -----------------------------
# World Map (HEX Colors)
# -----------------------------
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="ISO3",
    hover_name="Country",
    color_discrete_map=hex_map,
    title=f"Global Health Overview – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        projection_type="natural earth"
    ),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    margin=dict(t=50, b=0, l=0, r=0),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Country Details Section
# -----------------------------
st.markdown("---")
st.markdown("## 📊 Country Detailed Analysis")

country_df = df[df["Country"] == selected_country].sort_values("Year")
iso = country_df.iloc[0]["ISO3"]

latest = country_df[country_df["Year"] == year]

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)
k1.metric("HDI", round(latest["HDI"].values[0], 3))
k2.metric("Life Expectancy", round(latest["Life_Expectancy"].values[0], 1))
k3.metric("GDP per Capita", f"${int(latest['GDP_per_capita'].values[0])}")
k4.metric("Median Age", round(latest["Median_Age_Est"].values[0], 1))

st.markdown("---")

# ---- Line Charts ----
indicators = {
    "HDI": "HDI",
    "Life Expectancy": "Life_Expectancy",
    "GDP per Capita": "GDP_per_capita",
    "Gini Index": "Gini_Index",
    "COVID Deaths / mil": "COVID_Deaths"
}

cols = st.columns(2)

for i, (label, col) in enumerate(indicators.items()):
    fig_line = px.line(
        country_df,
        x="Year",
        y=col,
        markers=True,
        title=label
    )
    fig_line.update_layout(
        height=300,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        margin=dict(t=40, b=10, l=10, r=10)
    )

    with cols[i % 2]:
        st.plotly_chart(fig_line, use_container_width=True)
