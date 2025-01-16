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

with open(SCHEMA_PATH_EMDAT, "r") as schema_emdat:
    emdat_schema = json.load(schema_emdat)


emdat_df_raw = pd.read_csv(EMDAT_INPUT_CSV)

#print(emdat_df_raw.columns)

cleaned1_df = map_and_drop_columns(emdat_df_raw, EMDAT_MAPPING)

os.makedirs("./data_mid/emdat/cleaned_inspection", exist_ok=True)
cleaned1_df.to_csv("./data_mid/emdat/cleaned_inspection/emdat_cleaned.csv", index=False)