"""Disaster Events Dashboard Application."""

import base64
from pathlib import Path

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


def get_image_as_base64(file_path: str) -> str:
    """Return the base64 encoded string of an image given its file path.

    Args:
        file_path (str): The file path of the image to encode.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    with Path(file_path).open("rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode()


img_ifrc = get_image_as_base64("img/ifrc-logo.png")
img_ma = get_image_as_base64("img/MA-logo.png")
img_ocha = get_image_as_base64("img/OCHA_0.png")

st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 20px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }
    .header-container img {
        max-height: 180px;
        object-fit: contain;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="header-container">
        <img src="data:image/png;base64,{img_ifrc}" />
        <img src="data:image/png;base64,{img_ma}" style="max-height:140px;" />
        <img src="data:image/png;base64,{img_ocha}" />
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style="text-align: center; color: #21324B; font-size: 3em;">
        Disaster Events Dashboard
    </h1>
    """,
    unsafe_allow_html=True,
)
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
