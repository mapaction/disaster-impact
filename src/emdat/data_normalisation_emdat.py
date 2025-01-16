import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    EMDAT_MAPPING,
)

EMDAT_INPUT_CSV = "./data/emdat/emdat/public_emdat_custom_request_2024-11-28_cea79da6-3a0a-4ffe-aae1-8233b597b126.csv"
SCHEMA_PATH_EMDAT = "./src/emdat/emdat_schema.json"

def safe_cast_to_int(column: pd.Series) -> pd.Series:
    return column.apply(
        lambda x: int(x) if pd.notnull(x) and isinstance(x, (int, float)) and x == int(x) else pd.NA
    ).astype("Int64")

def safe_change_data_type(cleaned1_data: pd.DataFrame, json_schema: dict) -> pd.DataFrame:
    for column, properties in json_schema["properties"].items():
        if column in cleaned1_data.columns:
            column_type = properties.get("type")
            if "array" in column_type:
                cleaned1_data[column] = cleaned1_data[column].apply(
                    lambda x: x if isinstance(x, list) else [x] if pd.notnull(x) else []
                )
            elif "string" in column_type:
                cleaned1_data[column] = cleaned1_data[column].astype(str)
            elif "number" in column_type:
                cleaned1_data[column] = pd.to_numeric(cleaned1_data[column], errors="coerce")
            elif "integer" in column_type:
                cleaned1_data[column] = safe_cast_to_int(cleaned1_data[column])
            elif "null" in column_type:
                cleaned1_data[column] = cleaned1_data[column].where(cleaned1_data[column].notna(), None)
    return cleaned1_data

def fix_date_column(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    raw_date_col = mapping.get("Date")
    raw_year_col = mapping.get("Year")

    if raw_date_col in df.columns:
        df["Date"] = df[raw_date_col]

    return df

with open(SCHEMA_PATH_EMDAT, "r") as schema_emdat:
    emdat_schema = json.load(schema_emdat)

emdat_df_raw = pd.read_csv(EMDAT_INPUT_CSV)

print("Preview of raw data:")
print(emdat_df_raw.head())

cleaned1_df = map_and_drop_columns(emdat_df_raw, EMDAT_MAPPING)

cleaned1_df = fix_date_column(cleaned1_df, EMDAT_MAPPING)

cleaned2_df = safe_change_data_type(cleaned1_df, emdat_schema)

os.makedirs("./data_mid/emdat/cleaned_inspection", exist_ok=True)
cleaned2_df.to_csv("./data_mid/emdat/cleaned_inspection/emdat_cleaned.csv", index=False)

print("Preview of cleaned data:")
print(cleaned2_df.head())
