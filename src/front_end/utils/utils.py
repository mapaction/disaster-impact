"""Utility functions for the front-end of the dashboard."""

import base64
from pathlib import Path

import streamlit as st


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


def render_header(img_ifrc: str, img_ma: str, img_ocha: str) -> None:
    """Render the header section of the dashboard."""
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
