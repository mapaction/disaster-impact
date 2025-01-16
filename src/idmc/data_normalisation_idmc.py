import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    IDMC_MAPPING
)

IDMC_INPUT_CSV = "./data/idmc_idu/idus_all_flattened.csv"
SCHEMA_PATH_IDMC = "./src/idmc/idmc_schema.json"

with open(SCHEMA_PATH_IDMC, "r") as schema_idmc:
    idmc_schema = json.load(schema_idmc)

idmc_df_raw = pd.read_csv(IDMC_INPUT_CSV)
print("Preview of raw data:")
print(idmc_df_raw.head())