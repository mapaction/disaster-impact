"""This script reads the raw IFRC emergencies data from the Azure Blob Storage.

Cleans it, and saves the cleaned data as a CSV file for inspection.
"""

import json
import logging
from pathlib import Path

import pandas as pd

from src.data_consolidation.dictionary import IFRC_EME_MAPPING
from src.glide.data_normalisation_glide import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)
from src.utils.azure_blob_utils import read_blob_to_dataframe

IFRC_EME_INPUT_BLOB = "disaster-impact/raw/ifrc_dref/IFRC_emergencies.csv"
SCHEMA_PATH_IFRC_EME = "./src/ifrc_eme/ifrc_eme_schema.json"
EVENT_CODE_CSV = "./static_data/event_code_table.csv"

with Path(SCHEMA_PATH_IFRC_EME).open() as schema_ifrc_eme:
    ifrc_eme_schema = json.load(schema_ifrc_eme)


def clean_disaster_start_date(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Cleans the disaster start date column by removing the time part.

    Args:
        df (pd.DataFrame): The DataFrame containing the disaster data.
        column_name (str): The name of the column to clean.

    Returns:
        pd.DataFrame: The DataFrame with the cleaned disaster start date column.
    """
    if column_name in df.columns:
        df[column_name] = df[column_name].str.split("T").str[0]
    return df


def main() -> None:
    """Reads the raw IFRC emergencies data from the Azure Blob Storage."""
    try:
        ifrc_eme_df_raw = read_blob_to_dataframe(
            IFRC_EME_INPUT_BLOB,
            on_bad_lines="skip",
        )
    except (OSError, ValueError):
        error_message = "Error reading blob to dataframe"
        logging.exception(error_message)

    ifrc_eme_df_raw = clean_disaster_start_date(ifrc_eme_df_raw, "disaster_start_date")
    cleaned1_df = map_and_drop_columns(ifrc_eme_df_raw, IFRC_EME_MAPPING)
    cleaned2_df = change_data_type(cleaned1_df, ifrc_eme_schema)
    cleaned2_df["Date"] = pd.to_datetime(cleaned2_df["Date"], errors="coerce")
    cleaned2_df = normalize_event_type(cleaned2_df, EVENT_CODE_CSV)

    schema_order = list(ifrc_eme_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]

    Path("./data_mid_1/ifrc_eme").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/ifrc_eme/ifrc_eme_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
