import pandas as pd
import os
import json

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

with open(SCHEMA_PATH_GDACS, "r") as schema_gdacs:
    gdacs_schema = json.load(schema_gdacs)



gdacs_df_raw = pd.read_csv(GDACS_INPUT_CSV)
cleaned1_gdacs_df = map_and_drop_columns(gdacs_df_raw, GDACS_MAPPING)
cleaned2_gdacs_df = change_data_type(cleaned1_gdacs_df, gdacs_schema)
os.makedirs("./data_mid/gdacs/cleaned_inspaction", exist_ok=True)
cleaned2_gdacs_df.to_csv("./data_mid/gdacs/cleaned_inspaction/cleaned_gdacs.csv", index=False)