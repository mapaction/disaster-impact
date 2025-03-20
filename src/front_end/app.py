"""Disaster Events Dashboard Application."""

import pandas as pd
import streamlit as st

from utils.utils import (
    render_header,
    side_bar_title_style,
    sidebar_widget,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load disaster event data from a CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the disaster event data.
    """
    disaster_data = pd.read_csv("./output_data/streamlit_input_data_v2.csv")
    disaster_data.columns = disaster_data.columns.str.strip()
    disaster_data["Year"] = disaster_data["Year"].astype(int)
    return disaster_data


data = load_data()

render_header()


side_bar_title_style("Filters")

selected_country = sidebar_widget(
    "Select a country",
    st.sidebar.selectbox,
    options=["All", *sorted(data["Country"].unique().tolist())],
)

selected_event = sidebar_widget(
    "Select a disaster type",
    st.sidebar.selectbox,
    options=["All", *sorted(data["Event Type"].unique().tolist())],
)

min_year = 2000
max_year = int(data["Year"].max())

year_range = sidebar_widget(
    "Select Year Range",
    st.sidebar.slider,
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

min_val_sources = int(data["Nb Sources"].min())
max_val_sources = int(data["Nb Sources"].max())


number_of_sources = sidebar_widget(
    "Number of Sources",
    st.sidebar.slider,
    min_value=min_val_sources,
    max_value=max_val_sources,
    value=(min_val_sources, max_val_sources),
)

if st.sidebar.button("## Filter Data"):
    filtered_data = data.copy()

    if selected_country != "All":
        filtered_data = filtered_data[filtered_data["Country"] == selected_country]

    if selected_event != "All":
        filtered_data = filtered_data[filtered_data["Event"] == selected_event]

    filtered_data = filtered_data[
        (filtered_data["Year"] >= year_range[0])
        & (filtered_data["Year"] <= year_range[1])
    ]

    filtered_data["Year"] = filtered_data["Year"].astype(int).astype(str)

    filtered_data = filtered_data[
        (filtered_data["Nb Sources"] >= number_of_sources[0])
        & (filtered_data["Nb Sources"] <= number_of_sources[1])
    ]

    st.write("## Filtered Data")
    st.dataframe(filtered_data, width=1000, height=600)

    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )
