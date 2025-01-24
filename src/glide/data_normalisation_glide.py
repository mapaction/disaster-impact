import pandas as pd
import os
import json
from src.data_consolidation.dictionary import GLIDE_MAPPING
from src.utils.azure_blob_utils import read_blob_to_dataframe

GLIDE_INPUT_BLOB = "disaster-impact/raw/glide/glide_data_combined_all.csv"
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

def main():
    try:
        glide_df_raw = read_blob_to_dataframe(GLIDE_INPUT_BLOB)
    except Exception as e:
        print(f"Failed to load data from blob: {e}")
        exit(1)
    
    cleaned1_glide_df = map_and_drop_columns(glide_df_raw, GLIDE_MAPPING)
    cleaned2_glide_df = change_data_type(cleaned1_glide_df, glide_schema)
    os.makedirs("./data_mid/glide/cleaned_inspaction", exist_ok=True)
    output_file_path = "./data_mid/glide/cleaned_inspaction/cleaned_glide.csv"
    cleaned2_glide_df.to_csv(output_file_path, index=False)
    print(f"Cleaned GLIDE data saved for inspection at: {output_file_path}")

if __name__ == "__main__":
    main()
