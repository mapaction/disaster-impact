"""This script reads the raw EMDAT data from the blob, cleans it."""

import json
from io import StringIO
from pathlib import Path

import pandas as pd

from src.data_consolidation.dictionary import EMDAT_MAPPING
from src.utils.azure_blob_utils import read_blob_to_dataframe
from src.utils.util import (
    map_and_drop_columns,
    normalize_event_type,
)

EMDAT_INPUT_XLX_BLOB = (
    "disaster-impact/raw/emdat/"
    "public_emdat_custom_request_2024-11-28_"
    "cea79da6-3a0a-4ffe-aae1-8233b597b126.xlsx"
)
SCHEMA_PATH_EMDAT = "./src/emdat/emdat_schema.json"
EVENT_CODE_CSV = "./static_data/event_code_table.csv"


def safe_cast_to_int(
    column: pd.Series,
) -> pd.Series:
    """Safely cast a pandas Series to integers.

    This function converts each element in the
    given pandas Series to an integer if it is a valid integer or float
    and not null. If the element cannot be converted,
    it is replaced with pandas' NA value.

    Args:
        column (pd.Series): The input pandas Series to be cast to integers.

    Returns:
        pd.Series: A pandas Series with elements cast to integers or NA values.
    """
    return column.apply(
        lambda x: int(x)
        if pd.notna(x) and isinstance(x, int | float) and x == int(x)
        else pd.NA,
    ).astype("Int64")


def safe_change_data_type(
    cleaned1_data: pd.DataFrame,
    json_schema: dict,
) -> pd.DataFrame:
    """Safely changes the dt of columns in a DF based on a given JSON schema.

    Args:
        cleaned1_data (pd.DataFrame): The DF with data to be type-casted.
        json_schema (dict): The JSON schema defining
        the desired data types for each column.

    Returns:
        pd.DataFrame: The DataFrame with columns type-casted
        according to the JSON schema.
    """
    for column, properties in json_schema["properties"].items():
        if column in cleaned1_data.columns:
            column_type = properties.get("type")
            if "array" in column_type:
                cleaned1_data[column] = cleaned1_data[column].apply(
                    lambda x: ",".join(map(str, x))
                    if isinstance(x, list)
                    else (str(x) if pd.notna(x) else ""),
                )
            elif "string" in column_type:
                cleaned1_data[column] = cleaned1_data[column].astype(str)
            elif "number" in column_type:
                cleaned1_data[column] = pd.to_numeric(
                    cleaned1_data[column],
                    errors="coerce",
                )
            elif "integer" in column_type:
                cleaned1_data[column] = safe_cast_to_int(cleaned1_data[column])
            elif "null" in column_type:
                cleaned1_data[column] = cleaned1_data[column].where(
                    cleaned1_data[column].notna(),
                    None,
                )
    return cleaned1_data


def create_start_date(
    df: pd.DataFrame,
    year_col: str,
    month_col: str,
    day_col: str,
) -> pd.DataFrame:
    """Adds a 'Date' column to the DF by combining year, month, and day columns.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    year_col (str): The name of the column containing the year.
    month_col (str): The name of the column containing the month.
    day_col (str): The name of the column containing the day.

    Returns:
    pd.DataFrame: The DataFrame with the new 'Date' column.
    """
    df["Date"] = pd.to_datetime(
        {
            "year": df[year_col],
            "month": df[month_col].fillna(1).astype(int),
            "day": df[day_col].fillna(1).astype(int),
        },
        errors="coerce",
    )
    return df


def main() -> None:
    """Main function to clean the EMDAT data and save it to a CSV file."""
    excel_df = read_blob_to_dataframe(EMDAT_INPUT_XLX_BLOB)

    csv_buffer = StringIO()
    excel_df.to_csv(csv_buffer, index=False)
    emdat_input_csv = csv_buffer.getvalue()

    emdat_df_raw = pd.read_csv(StringIO(emdat_input_csv))

    with Path(SCHEMA_PATH_EMDAT).open() as schema_emdat:
        emdat_schema = json.load(schema_emdat)

    cleaned1_df = map_and_drop_columns(emdat_df_raw, EMDAT_MAPPING)
    cleaned1_df = create_start_date(
        cleaned1_df,
        year_col="Year",
        month_col="Month",
        day_col="Day",
    )
    cleaned2_df = safe_change_data_type(cleaned1_df, emdat_schema)
    cleaned2_df["Date"] = pd.to_datetime(cleaned2_df["Date"], errors="coerce")
    cleaned2_df = normalize_event_type(cleaned2_df, EVENT_CODE_CSV)
    schema_order = list(emdat_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]

    Path("./data_mid_1/emdat/").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/emdat/emdat_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
