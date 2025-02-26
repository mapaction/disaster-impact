"""This script reads raw GLIDE data from an Azure Blob Storage container.

Cleans it, and saves the cleaned data to a CSV file.
"""

import json
from pathlib import Path

import pandas as pd

from src.data_consolidation.dictionary import GLIDE_MAPPING
from src.utils.azure_blob_utils import read_blob_to_dataframe
from src.utils.util import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)

GLIDE_INPUT_BLOB = "disaster-impact/raw/glide/glide_data_combined_all.csv"
SCHEMA_PATH_GLIDE = "./src/glide/glide_schema.json"
EVENT_CODE_CSV = "./static_data/event_code_table.csv"

with Path(SCHEMA_PATH_GLIDE).open() as schema_glide:
    glide_schema = json.load(schema_glide)


def main() -> None:
    """Main function to clean the GLIDE data and save it to a CSV file."""
    glide_df_raw = read_blob_to_dataframe(GLIDE_INPUT_BLOB)

    cleaned1_glide_df = map_and_drop_columns(glide_df_raw, GLIDE_MAPPING)
    cleaned2_glide_df = change_data_type(cleaned1_glide_df, glide_schema)

    cleaned2_glide_df["Date"] = pd.to_datetime(
        cleaned2_glide_df["Date"],
        errors="coerce",
    )

    cleaned2_glide_df = normalize_event_type(cleaned2_glide_df, EVENT_CODE_CSV)
    schema_order = list(glide_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_glide_df.columns]
    remaining_columns = [
        col for col in cleaned2_glide_df.columns if col not in schema_order
    ]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_glide_df = cleaned2_glide_df[final_columns_order]

    Path("./data_mid_1/glide").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/glide/glide_mid1.csv"
    cleaned2_glide_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
