import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    CERF_MAPPING,
)

CERF_INPUT_CSV = "./data/cerf/cerf_emergency_data_dynamic_web_scrape.csv"
SCHEMA_PATH_CERF = "./src/cerf/cerf_schema.json"

with open(SCHEMA_PATH_CERF, "r") as schema_cerf:
    cerf_schema = json.load(schema_cerf)

cerf_df_raw = pd.read_csv(CERF_INPUT_CSV)

print("Preview of raw data:")
print(cerf_df_raw.head())