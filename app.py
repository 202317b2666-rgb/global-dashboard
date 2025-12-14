import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import streamlit_shadcn_ui as ui

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("final_with_socio_cleaned.csv")
    return df

df = load_data()

year = st.slider(
    "Select Year",
    int(df["Year"].min()),
    int(df["Year"].max()),
    int(df["Year"].max())
)

year_df = df[df["Year"] == year]

fig = px.choropleth(
    year_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis"
)

selected = plotly_events(fig, click_event=True, key="map")

if selected:
    iso = selected[0]["location"]
    row = year_df[year_df["ISO3"] == iso].iloc[0]

    ui.popover(
        label=f"📊 {row['Country']} ({year})",
        content=f"""
        **HDI:** {row['HDI']:.3f}  
        **Life Expectancy:** {row['Life_Expectancy']:.1f}  
        **GDP per Capita:** ${row['GDP_per_capita']:,.0f}  
        **Median Age:** {row['Median_Age']:.1f}
        """,
        key="country_popover"
    )
else:
    st.info("👆 Click a country on the map")
