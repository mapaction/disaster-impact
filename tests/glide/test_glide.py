"""Tests for the data_normalisation_glide module."""

import pandas as pd

from src.glide.data_normalisation_glide import map_and_drop_columns


def test_map_and_drop_columns() -> None:
    """Test the map_and_drop_columns function."""

    raw_data = pd.DataFrame(
        {
            "old_column1": [1, 2, 3],
            "old_column2": [4, 5, 6],
            "old_column3": [7, 8, 9],
        },
    )

    mapping = {
        "new_column1": "old_column1",
        "new_column2": "old_column2",
    }

    expected = pd.DataFrame(
        {
            "new_column1": [1, 2, 3],
            "new_column2": [4, 5, 6],
        },
    )

    result = map_and_drop_columns(raw_data, mapping)

    pd.testing.assert_frame_equal(result, expected)
