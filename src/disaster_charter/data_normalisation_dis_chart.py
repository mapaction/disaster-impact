import pandas as pd
import json
import os


from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    DISASTER_CHARTER_MAPPING,
)

DISASTER_CHARTER_INPUT_CSV = "./data/disaster-charter/disaster_activations_boosted_dec.csv"
SCHEMA_PATH_DISASTER_CHARTER = "./src/disaster_charter/disaster_charter_schema.json"

with open(SCHEMA_PATH_DISASTER_CHARTER, "r") as schema_disaster_charter:
    disaster_schema = json.load(schema_disaster_charter)

disaster_charter_df_raw = pd.read_csv(DISASTER_CHARTER_INPUT_CSV)

#print(disaster_charter_df_raw.columns)

cleaned1_df = map_and_drop_columns(disaster_charter_df_raw, DISASTER_CHARTER_MAPPING)
cleaned2_df = change_data_type(cleaned1_df, disaster_schema)
os.makedirs("./data_mid/disaster_charter/cleaned_inspection", exist_ok=True)
cleaned2_df.to_csv("./data_mid/disaster_charter/cleaned_inspection/disaster_charter_cleaned.csv", index=False)