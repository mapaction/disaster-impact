import pandas as pd
import json
import os
from io import StringIO

from src.glide.data_normalisation_glide import map_and_drop_columns
from src.data_consolidation.dictionary import EMDAT_MAPPING
from src.utils.azure_blob_utils import read_blob_to_dataframe

EMDAT_INPUT_XLX_BLOB = "disaster-impact/raw/emdat/public_emdat_custom_request_2024-11-28_cea79da6-3a0a-4ffe-aae1-8233b597b126.xlsx"
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

def create_start_date(df: pd.DataFrame, year_col: str, month_col: str, day_col: str) -> pd.DataFrame:
    df["Date"] = pd.to_datetime(
        {
            "year": df[year_col],
            "month": df[month_col].fillna(1).astype(int),
            "day": df[day_col].fillna(1).astype(int)
        },
        errors="coerce"
    )
    return df

if __name__ == "__main__":
    try:
        excel_df = read_blob_to_dataframe(EMDAT_INPUT_XLX_BLOB)
    except Exception as e:
        print(f"Failed to load Excel data from blob: {e}")
        exit(1)

    csv_buffer = StringIO()
    excel_df.to_csv(csv_buffer, index=False)
    emdat_input_csv = csv_buffer.getvalue()

    emdat_df_raw = pd.read_csv(StringIO(emdat_input_csv))

    with open(SCHEMA_PATH_EMDAT, "r") as schema_emdat:
        emdat_schema = json.load(schema_emdat)

    cleaned1_df = map_and_drop_columns(emdat_df_raw, EMDAT_MAPPING)
    cleaned1_df = create_start_date(cleaned1_df, year_col="Year", month_col="Month", day_col="Day")
    cleaned2_df = safe_change_data_type(cleaned1_df, emdat_schema)

    os.makedirs("./data_mid/emdat/cleaned_inspection", exist_ok=True)
    output_file_path = "./data_mid/emdat/cleaned_inspection/emdat_cleaned.csv"
    cleaned2_df.to_csv(output_file_path, index=False)

    print(f"Cleaned EMDAT data saved for inspection at: {output_file_path}")
