import pandas as pd
import os
import json
import ast

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    GDACS_MAPPING,
)

GDACS_INPUT_CSV = "./data/gdacs_all_types_yearly_v3_fast/combined_gdacs_data.csv"
SCHEMA_PATH_GDACS = "./src/gdacs/gdacs_schema.json"

def extract_lat_lon_from_existing_columns(df: pd.DataFrame, coord_col: str = 'coordinates', lat_col: str = 'Latitude', lon_col: str = 'Longitude') -> pd.DataFrame:
    if lat_col in df.columns:
        def extract_lat(coords):
            if isinstance(coords, list) and len(coords) == 2:
                return coords[1]
            return None
        df[lat_col] = df[lat_col].apply(extract_lat)

    if lon_col in df.columns:
        def extract_lon(coords):
            if isinstance(coords, list) and len(coords) == 2:
                return coords[0]
            return None
        df[lon_col] = df[lon_col].apply(extract_lon)

    return df


with open(SCHEMA_PATH_GDACS, "r") as schema_gdacs:
    gdacs_schema = json.load(schema_gdacs)

gdacs_df_raw = pd.read_csv(GDACS_INPUT_CSV)
cleaned1_gdacs_df = map_and_drop_columns(gdacs_df_raw, GDACS_MAPPING)
# cleaned1_gdacs_df = extract_lat_lon_from_existing_columns(cleaned1_gdacs_df, coord_col='coordinates', lat_col='Latitude', lon_col='Longitude')
# cleaned2_gdacs_df = change_data_type(cleaned1_gdacs_df, gdacs_schema)
os.makedirs("./data_mid/gdacs/cleaned_inspaction", exist_ok=True)
cleaned1_gdacs_df.to_csv("./data_mid/gdacs/cleaned_inspaction/cleaned_gdacs.csv", index=False)
