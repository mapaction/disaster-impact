"""Gdacs data normalisation script."""

import ast
import json
import re
from pathlib import Path

import pandas as pd
import pycountry

from src.data_consolidation.dictionary import GDACS_MAPPING
from src.utils.azure_blob_utils import combine_csvs_from_blob_dir
from src.utils.util import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)

EVENT_CODE_CSV = "./static_data/event_code_table.csv"
COORDINATE_PAIR_LENGTH = 2
SCHEMA_PATH_GDACS = "./src/gdacs/gdacs_schema.json"


def combine_csvs_from_blob(blob_dir: str) -> pd.DataFrame:
    """Combines multiple CSV files.

    Args:
        blob_dir (str): The directory path in the blob storage where the CSV files are.

    Returns:
        pd.DataFrame: A DataFrame containing the combined data from all the CSV files.
    """
    return combine_csvs_from_blob_dir(blob_dir)


def split_coordinates(
    df: pd.DataFrame,
    coord_col: str = "coordinates",
    lat_col: str = "Latitude",
    lon_col: str = "Longitude",
) -> pd.DataFrame:
    """Splits a DataFrame column containing coordinate pairs.

    Args:
        df (pd.DataFrame): The input DataFrame containing the coordinates.
        coord_col (str): The name of the column with coordinate pairs.
        Default is 'coordinates'.
        lat_col (str): The name of the new column for latitude values.
        Default is 'Latitude'.
        lon_col (str): The name of the new column for longitude values.
        Default is 'Longitude'.

    Returns:
        pd.DataFrame: The DataFrame with added latitude and longitude columns.
    """
    if coord_col in df.columns:
        df[coord_col] = df[coord_col].apply(
            lambda x: ast.literal_eval(x)
            if isinstance(x, str) and x.startswith("[")
            else x,
        )
        df[lat_col] = df[coord_col].apply(
            lambda x: x[1]
            if isinstance(x, list) and len(x) == COORDINATE_PAIR_LENGTH
            else None,
        )
        df[lon_col] = df[coord_col].apply(
            lambda x: x[0]
            if isinstance(x, list) and len(x) == COORDINATE_PAIR_LENGTH
            else None,
        )
    return df


def enrich_country_data(df: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
    """Enriches the given DataFrame with country data.

    This function performs the following operations:
    1. Extracts country names from the 'Event_Name' column if 'Country' is missing.
    2. Extracts country codes from the 'Country' column if 'Country_Code' is missing.
    3. Converts country names to ISO3 country codes if 'Country_Code' is still missing.

    Args:
        df (pd.DataFrame): The input DataFrame containing disaster event data.

    Returns:
        pd.DataFrame: The enriched DataFrame with updated
        'Country' and 'Country_Code' columns.
    """
    if "Country" in df.columns and "Event_Name" in df.columns:

        def extract_country_from_event_name(row: str) -> str:
            if pd.isna(row["Country"]) and isinstance(row["Event_Name"], str):
                match = re.search(r"\bin\s+([A-Za-z0-9\s\(\)-]+)$", row["Event_Name"])
                if match:
                    return match.group(1).strip()
            return row["Country"]

        df["Country"] = df.apply(extract_country_from_event_name, axis=1)

    if "Country" in df.columns and "Country_Code" in df.columns:

        def maybe_extract_country_code(row: str) -> str:
            if pd.isna(row["Country_Code"]) and isinstance(row["Country"], str):
                match = re.search(r"\(([^)]*)\)", row["Country"])
                if match:
                    return match.group(1).strip()
            return row["Country_Code"]

        df["Country_Code"] = df.apply(maybe_extract_country_code, axis=1)
        df["Country"] = df["Country"].str.replace(r"\s*\([^)]*\)$", "", regex=True)

    def get_iso3_from_country_name(country_name: str) -> None:
        """Convert a country name to its ISO 3166-1 alpha-3 country code.

        Args:
            country_name (str): The name of the country to convert.

        Returns:
            str or None: The ISO 3166-1 alpha-3 country code if found, otherwise None.
        """
        if country_name and isinstance(country_name, str):
            try:
                matches = pycountry.countries.search_fuzzy(country_name)
                if matches:
                    return matches[0].alpha_3
            except LookupError:
                return None
        return None

    if "Country" in df.columns and "Country_Code" in df.columns:
        df["Country_Code"] = df.apply(
            lambda row: row["Country_Code"]
            if pd.notna(row["Country_Code"])
            else get_iso3_from_country_name(row["Country"]),
            axis=1,
        )

    return df


def main() -> None:
    """Main function to clean the GDACS data and save it to a CSV file."""
    blob_dir = "disaster-impact/raw/gdacs/v2/"

    gdacs_df_raw = combine_csvs_from_blob(blob_dir)
    gdacs_df_raw = split_coordinates(
        gdacs_df_raw,
        coord_col="coordinates",
        lat_col="Latitude",
        lon_col="Longitude",
    )

    with Path(SCHEMA_PATH_GDACS).open() as schema_gdacs:
        gdacs_schema = json.load(schema_gdacs)

    cleaned1_gdacs_df = map_and_drop_columns(gdacs_df_raw, GDACS_MAPPING)
    cleaned1_gdacs_df = enrich_country_data(cleaned1_gdacs_df)
    cleaned2_gdacs_df = change_data_type(cleaned1_gdacs_df, gdacs_schema)
    cleaned2_gdacs_df["Date"] = (
        pd.to_datetime(cleaned2_gdacs_df["Date"], errors="coerce")
    ).dt.date
    cleaned2_gdacs_df["End_Date"] = (
        pd.to_datetime(cleaned2_gdacs_df["End_Date"], errors="coerce")
    ).dt.date
    cleaned2_gdacs_df = normalize_event_type(cleaned2_gdacs_df, EVENT_CODE_CSV)
    schema_order = list(gdacs_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_gdacs_df.columns]
    remaining_columns = [
        col for col in cleaned2_gdacs_df.columns if col not in schema_order
    ]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_gdacs_df = cleaned2_gdacs_df[final_columns_order]
    Path("./data_mid_1/gdacs/").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/gdacs/gdacs_mid1.csv"
    cleaned2_gdacs_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
