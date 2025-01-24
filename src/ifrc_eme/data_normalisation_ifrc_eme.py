import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import map_and_drop_columns, change_data_type
from src.data_consolidation.dictionary import IFRC_EME_MAPPING
from src.utils.azure_blob_utils import read_blob_to_dataframe

IFRC_EME_INPUT_BLOB = "disaster-impact/raw/ifrc_dref/IFRC_emergencies.csv"
SCHEMA_PATH_IFRC_EME = "./src/ifrc_eme/ifrc_eme_schema.json"

with open(SCHEMA_PATH_IFRC_EME, "r") as schema_ifrc_eme:
    ifrc_eme_schema = json.load(schema_ifrc_eme)

def clean_disaster_start_date(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if column_name in df.columns:
        df[column_name] = df[column_name].str.split('T').str[0]
    return df

def main():
    
    try:
        ifrc_eme_df_raw = read_blob_to_dataframe(IFRC_EME_INPUT_BLOB, on_bad_lines="skip")
    except Exception as e:
        print(f"Failed to load data from blob: {e}")
        exit(1)

    ifrc_eme_df_raw = clean_disaster_start_date(ifrc_eme_df_raw, 'disaster_start_date')
    cleaned1_df = map_and_drop_columns(ifrc_eme_df_raw, IFRC_EME_MAPPING)
    cleaned2_df = change_data_type(cleaned1_df, ifrc_eme_schema)

    os.makedirs("./data_mid/ifrc_eme/cleaned_inspection", exist_ok=True)
    output_file_path = "./data_mid/ifrc_eme/cleaned_inspection/cleaned_ifrc_eme.csv"
    cleaned2_df.to_csv(output_file_path, index=False)

    print(f"Cleaned IFRC emergencies data saved for inspection at: {output_file_path}")

if __name__ == "__main__":
    main()
