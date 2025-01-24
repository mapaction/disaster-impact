import pandas as pd
import os
import json
import re
import pycountry
from io import BytesIO

from src.glide.data_normalisation_glide import map_and_drop_columns, change_data_type
from src.data_consolidation.dictionary import GDACS_MAPPING
from src.utils.azure_blob_utils import combine_csvs_from_blob_dir

def combine_csvs_from_blob(blob_dir: str) -> pd.DataFrame:
    combined_df = combine_csvs_from_blob_dir(blob_dir)
    return combined_df

def split_coordinates(df: pd.DataFrame, coord_col: str = 'coordinates', lat_col: str = 'Latitude', lon_col: str = 'Longitude') -> pd.DataFrame:
    if coord_col in df.columns:
        df[coord_col] = df[coord_col].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else x)
        df[lat_col] = df[coord_col].apply(lambda x: x[1] if isinstance(x, list) and len(x) == 2 else None)
        df[lon_col] = df[coord_col].apply(lambda x: x[0] if isinstance(x, list) and len(x) == 2 else None)
    return df

def enrich_country_data(df: pd.DataFrame) -> pd.DataFrame:
    if 'Country' in df.columns and 'Event_Name' in df.columns:
        def extract_country_from_event_name(row):
            if pd.isna(row['Country']) and isinstance(row['Event_Name'], str):
                match = re.search(r'\bin\s+([A-Za-z0-9\s\(\)-]+)$', row['Event_Name'])
                if match:
                    return match.group(1).strip()
            return row['Country']

        df['Country'] = df.apply(extract_country_from_event_name, axis=1)

    if 'Country' in df.columns and 'Country_Code' in df.columns:
        def maybe_extract_country_code(row):
            if pd.isna(row['Country_Code']) and isinstance(row['Country'], str):
                match = re.search(r'\(([^)]*)\)', row['Country'])
                if match:
                    return match.group(1).strip()
            return row['Country_Code']

        df['Country_Code'] = df.apply(maybe_extract_country_code, axis=1)
        df['Country'] = df['Country'].str.replace(r'\s*\([^)]*\)$', '', regex=True)

    def get_iso3_from_country_name(country_name):
        if country_name and isinstance(country_name, str):
            try:
                matches = pycountry.countries.search_fuzzy(country_name)
                if matches:
                    return matches[0].alpha_3
            except LookupError:
                return None
        return None

    if 'Country' in df.columns and 'Country_Code' in df.columns:
        df['Country_Code'] = df.apply(
            lambda row: row['Country_Code'] \
                        if pd.notna(row['Country_Code']) \
                        else get_iso3_from_country_name(row['Country']),
            axis=1
        )

    return df

if __name__ == "__main__":
    blob_dir = "disaster-impact/raw/gdacs/v2/"
    SCHEMA_PATH_GDACS = "./src/gdacs/gdacs_schema.json"

    try:
        gdacs_df_raw = combine_csvs_from_blob(blob_dir)
    except Exception as e:
        print(f"Failed to combine CSVs from blob directory: {e}")
        exit(1)

    gdacs_df_raw = split_coordinates(gdacs_df_raw, coord_col='coordinates', lat_col='Latitude', lon_col='Longitude')

    with open(SCHEMA_PATH_GDACS, "r") as schema_gdacs:
        gdacs_schema = json.load(schema_gdacs)

    cleaned1_gdacs_df = map_and_drop_columns(gdacs_df_raw, GDACS_MAPPING)
    cleaned1_gdacs_df = enrich_country_data(cleaned1_gdacs_df)
    cleaned2_gdacs_df = change_data_type(cleaned1_gdacs_df, gdacs_schema)

    os.makedirs("./data_mid/gdacs/cleaned_inspection", exist_ok=True)
    output_file_path = "./data_mid/gdacs/cleaned_inspection/cleaned_gdacs.csv"
    cleaned2_gdacs_df.to_csv(output_file_path, index=False)

    print(f"Cleaned GDACS data saved for inspection at: {output_file_path}")
