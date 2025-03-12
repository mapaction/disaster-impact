"""Disaster Events Dashboard Application."""

import pandas as pd
import streamlit as st


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load disaster event data from a CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the disaster event data.
    """
    disaster_data = pd.read_csv("./output_data/disaster_database_dummy_data.csv")
    disaster_data.columns = disaster_data.columns.str.strip()
    disaster_data["Year"] = disaster_data["Year"].astype(int)
    return disaster_data


data = load_data()

st.title("Disaster Events Dashboard")
st.sidebar.header("Filters")

countries = sorted(data["Country"].unique().tolist())
selected_country = st.sidebar.selectbox(
    "Select a country",
    options=["All", *countries],
)

event_types = sorted(data["Event"].unique().tolist())
selected_event = st.sidebar.selectbox(
    "Select a disaster type",
    options=["All", *event_types],
)

min_year = int(data["Year"].min())
max_year = int(data["Year"].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (min_year, max_year),
)

if st.sidebar.button("Filter Data"):
    filtered_data = data.copy()

    if selected_country != "All":
        filtered_data = filtered_data[filtered_data["Country"] == selected_country]

    if selected_event != "All":
        filtered_data = filtered_data[filtered_data["Event"] == selected_event]

    filtered_data = filtered_data[
        (filtered_data["Year"] >= year_range[0])
        & (filtered_data["Year"] <= year_range[1])
    ]

    st.write("### Filtered Data")
    st.dataframe(filtered_data)

    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )
