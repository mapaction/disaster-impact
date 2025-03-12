"""Utility functions for the front-end of the dashboard."""

import base64
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar

import streamlit as st

P = ParamSpec("P")
R = TypeVar("R")


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


def render_header() -> None:
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
        """
        <h1 style="text-align: center; color: #21324B; font-size: 3em;">
            Disaster Events Dashboard
        </h1>
        """,
        unsafe_allow_html=True,
    )


def side_bar_title_style(text: str) -> None:
    """Render a custom styled sidebar header with the given text."""
    st.sidebar.markdown(
        f"""
<div style="font-size:30px; font-weight:bold; color:#21324B; margin-bottom:20px;">
    {text}
</div>
""",
        unsafe_allow_html=True,
    )


def sidebar_widget(
    label: str,
    widget_func: Callable[P, R],
    **widget_kwargs: P.kwargs,
) -> R:
    """Render a custom-styled label for a sidebar widget and call the widget.

    The widget receives the label (so it isn't empty) but it is hidden.
    """
    st.sidebar.markdown(
        f"""
<div style="font-size:20px; font-weight:bold; color:#21324B; margin-bottom:5px;">
    {label}
</div>
""",
        unsafe_allow_html=True,
    )

    return widget_func(
        label=label,
        label_visibility="collapsed",
        **widget_kwargs,
    )
