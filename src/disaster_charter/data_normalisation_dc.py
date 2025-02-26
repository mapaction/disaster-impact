"""Data normalisation for the Disaster Charter dataset."""

import json
import re
from pathlib import Path

import pandas as pd

from src.data_consolidation.dictionary import (
    DISASTER_CHARTER_MAPPING,
)
from src.utils.azure_blob_utils import read_blob_to_dataframe
from src.utils.util import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)

SCHEMA_PATH_DISASTER_CHARTER = "./src/disaster_charter/disaster_charter_schema.json"
BLOB_NAME = (
    "disaster-impact/raw/disaster-charter/charter_activations_web_scrape_2000_2024.csv"
)
EVENT_CODE_CSV = "./static_data/event_code_table.csv"


def extract_event_type_from_event_name(
    df: pd.DataFrame,
    event_name_col: str = "Event_Name",
    event_type_col: str = "Event_Type",
) -> pd.DataFrame:
    """Extracts the ET from the EN if the event type is missing or empty.

    Args:
        df (pd.DataFrame): The DataFrame containing event data.
        event_name_col (str): The column name for event names. Default is 'Event_Name'.
        event_type_col (str): The column name for event types. Default is 'Event_Type'.

    Returns:
        pd.DataFrame: The DataFrame with the event type column updated.
    """
    if event_name_col in df.columns and event_type_col in df.columns:

        def extract_event_type(row: pd.Series) -> str | None:
            if (
                pd.isna(
                    row[event_type_col],
                )
                or not row[event_type_col]
            ) and isinstance(
                row[event_name_col],
                str,
            ):
                match = re.search(r"^(.*?)\s+in\s+", row[event_name_col])
                if match:
                    return match.group(1).strip()
            return row[event_type_col]

        df[event_type_col] = df.apply(extract_event_type, axis=1)
    return df


def remove_float_suffix(value: str | list) -> str | list:
    """Convert float values to strings without decimal points if they are whole numbers.

    Args:
        value (float, list): A float or a list of floats to be processed.

    Returns:
        str, list: A string or a list of
    strings with whole number floats converted to integers.
    """
    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            if isinstance(item, float) and item.is_integer():
                cleaned_list.append(str(int(item)))
            else:
                cleaned_list.append(str(item))
        return cleaned_list
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    """Normalises the Disaster Charter dataset."""
    with Path(SCHEMA_PATH_DISASTER_CHARTER).open() as schema_disaster_charter:
        disaster_schema = json.load(schema_disaster_charter)

    disaster_charter_df_raw = read_blob_to_dataframe(BLOB_NAME)

    cleaned1_df = map_and_drop_columns(
        disaster_charter_df_raw,
        DISASTER_CHARTER_MAPPING,
    )
    cleaned1_df = extract_event_type_from_event_name(
        cleaned1_df,
        event_name_col="Event_Name",
        event_type_col="Event_Type",
    )
    cleaned2_df = change_data_type(cleaned1_df, disaster_schema)
    cleaned2_df["Date"] = pd.to_datetime(cleaned2_df["Date"], errors="coerce")
    cleaned2_df = normalize_event_type(cleaned2_df, EVENT_CODE_CSV)
    schema_order = list(disaster_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]

    if "Source_Event_IDs" in cleaned2_df.columns:
        cleaned2_df["Source_Event_IDs"] = cleaned2_df["Source_Event_IDs"].apply(
            remove_float_suffix,
        )

    Path("./data_mid_1/disaster_charter/").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/disaster_charter/disaster_charter_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
