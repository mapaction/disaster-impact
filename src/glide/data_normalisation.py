import pandas as pd
import os
import json

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    GLIDE_MAPPING,
    GDACS_MAPPING,
    DISASTER_CHARTER_MAPPING,
    EMDAT_MAPPING,
    IDMC_MAPPING,
    CERF_MAPPING,
    IFRC_EME_MAPPING,
)

GLIDE_INPUT_CSV = "./data/glide/glide_data_combined_all.csv"
SCHEMA_PATH_GLIDE = "./src/glide/glide_schema.json"

with open(SCHEMA_PATH_GLIDE, "r") as schema_glide:
    glide_schema = json.load(schema_glide)


def map_and_drop_columns(raw_data: pd.DataFrame, dictionary: dict) -> pd.DataFrame:
    rename_mapping = {value: key for key, value in dictionary.items() if value}
    cleaned_data = raw_data[list(rename_mapping.keys())].rename(columns=rename_mapping)
    return cleaned_data

def change_data_type(cleaned1_data: pd.DataFrame, json_schema: dict) -> pd.DataFrame:
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
                cleaned1_data[column] = pd.to_numeric(cleaned1_data[column], errors="coerce").astype("Int64")
            elif "null" in column_type:
                cleaned1_data[column] = cleaned1_data[column].where(cleaned1_data[column].notna(), None)
    return cleaned1_data

glide_df_raw = pd.read_csv(GLIDE_INPUT_CSV)
cleaned1_glide_df = map_and_drop_columns(glide_df_raw, GLIDE_MAPPING)
cleaned2_glide_df = change_data_type(cleaned1_glide_df, glide_schema)
os.makedirs("./data_mid/glide/cleaned_inspaction", exist_ok=True)
cleaned2_glide_df.to_csv("./data_mid/glide/cleaned_inspaction/cleaned_glide.csv", index=False)