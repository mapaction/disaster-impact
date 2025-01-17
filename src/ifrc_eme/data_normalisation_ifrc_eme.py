import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    IFRC_EME_MAPPING,
)

IFRC_EME_INPUT_CSV = "./data/IFRC_eme/IFRC_emergencies.csv"
SCHEMA_PATH_IFRC_EME = "./src/ifrc_eme/ifrc_eme_schema.json"

with open(SCHEMA_PATH_IFRC_EME, "r") as schema_ifrc_eme:
    ifrc_eme_schema = json.load(schema_ifrc_eme)

def clean_disaster_start_date(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if column_name in df.columns:
        df[column_name] = df[column_name].str.split('T').str[0]  # Extract part before 'T'
    return df

ifrc_eme_df_raw = pd.read_csv(IFRC_EME_INPUT_CSV, on_bad_lines="skip")
ifrc_eme_df_raw = clean_disaster_start_date(ifrc_eme_df_raw, 'disaster_start_date')
cleaned1_df = map_and_drop_columns(ifrc_eme_df_raw, IFRC_EME_MAPPING)
# print("Preview of cleaned data:")
# print(cleaned1_df.head())
cleaned2_df = change_data_type(cleaned1_df, ifrc_eme_schema)
os.makedirs("./data_mid/ifrc_eme/cleaned_inspection", exist_ok=True)
cleaned2_df.to_csv("./data_mid/ifrc_eme/cleaned_inspection/cleaned_ifrc_eme.csv", index=False)
