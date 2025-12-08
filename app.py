import pandas as pd
import plotly.express as px

# Load the cleaned HEX CSV
hex_df = pd.read_csv("HEX_clean.csv")

# If your app uses a color key
hex_df["color_key"] = hex_df["figma_hex"]

# Continue with your Plotly map
fig = px.choropleth(
    hex_df,
    locations="iso_alpha",
    color="color_key",
    hover_name="country",
    color_discrete_map="identity",
    projection="natural earth"
)
fig.show()
