import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# ... (Keep the imports, Init, Load Data, and Dialog Function from the last answer) ...

# -----------------------------
# Dialog Function ( The Popup )
# -----------------------------
# Note: The function signature must remain the same
@st.dialog("Country Overview")
def show_country_details(iso_code):
    """
    Renders the charts inside the Streamlit dialog modal.
    """
    # ... (Keep the content of this function exactly the same) ...
    country_data = df[df["ISO3"] == iso_code]
    
    if country_data.empty:
        st.warning("No detailed data available for this country.")
        return

    country_name = country_data.iloc[0]["Country"]
    st.header(country_name)

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

    for i, (title, col_name) in enumerate(indicators.items()):
        if col_name in country_data.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=country_data["Year"],
                y=country_data[col_name],
                mode="lines+markers",
                line=dict(color='#00CC96', width=2),
                marker=dict(size=4)
            ))

            fig_line.update_layout(
                title=dict(text=title, font=dict(size=14)),
                template="plotly_dark",
                height=200,
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis=dict(title=None, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#333'),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            with cols[i % 2]:
                st.plotly_chart(fig_line, use_container_width=True)


# -----------------------------
# Main Layout (Starts here)
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🌍 Global Health Dashboard</h2>", unsafe_allow_html=True)

# Year Slider
# ... (Keep the slider code) ...
year = st.slider(
    "Select Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1
)

# Filter Data for Map
map_df = df[df["Year"] == year]

# Create Map
# ... (Keep the Plotly figure creation code) ...
fig = px.choropleth(
    map_df,
    locations="ISO3",
    color="HDI",
    hover_name="Country",
    color_continuous_scale="Viridis",
    range_color=[0, 1],
    title=f"Global HDI Map – {year}"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="white",
        showocean=True,
        oceancolor="#0E1117",
        showland=True,
        landcolor="#1a1a1a",
        projection_type="natural earth" 
    ),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    margin=dict(t=50, b=0, l=0, r=0),
    coloraxis_colorbar=dict(title="HDI")
)

# ----------------------------------------------------
# Use Native Plotly Click Event & Session State (THE FIX)
# ----------------------------------------------------

# 1. Initialize session state variable to store selected ISO code
if 'selected_iso' not in st.session_state:
    st.session_state.selected_iso = None

# 2. Define the callback function that runs on map click
def handle_map_selection():
    """
    Callback runs when the map selection changes.
    The selection data is automatically stored in st.session_state["global_map"].
    """
    selection = st.session_state.get("global_map")
    
    if selection and selection.get("points"):
        # Extract the ISO code from the clicked point
        clicked_iso = selection["points"][0]["location"]
        # Update the session state
        st.session_state.selected_iso = clicked_iso
    else:
        # If no points are selected (e.g., user clicked blank space)
        st.session_state.selected_iso = None

# 3. Render the Map with the callback
st.plotly_chart(
    fig, 
    use_container_width=True, 
    on_select=handle_map_selection, # Runs the function above on click
    selection_mode="points",
    key="global_map" # The key where selection data is stored
)

# 4. Trigger Dialog based on Session State
if st.session_state.selected_iso:
    # We call the dialog function directly with the ISO code
    show_country_details(st.session_state.selected_iso)
    
    # IMPORTANT: The st.dialog includes a native 'X' button. 
    # When the user clicks it, st.dialog handles hiding itself. 
    # We need to manually clear the session state to prevent it from re-opening on the next interaction.
    # However, since st.dialog does NOT trigger a rerun on close, we leave this line out for now
    # and rely on the next click to reset selected_iso via the handle_map_selection callback.
    pass
