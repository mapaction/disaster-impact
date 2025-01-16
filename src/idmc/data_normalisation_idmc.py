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

# idmc_df_raw = idmc_df_raw.applymap(
#     lambda x: x.replace(";", "-") if isinstance(x, str) else x
# )
idmc_df_raw = idmc_df_raw.apply(
    lambda row: row.map(lambda x: x.replace(";", "-") if isinstance(x, str) else x), axis=1
)
# print("Preview of raw data:")
# print(idmc_df_raw.head())

cleaned1_df = map_and_drop_columns(idmc_df_raw, IDMC_MAPPING)
cleaned2_df = change_data_type(cleaned1_df, idmc_schema)
os.makedirs("./data_mid/idmc_idu/cleaned_inspection", exist_ok=True)
cleaned2_df.to_csv("./data_mid/idmc_idu/cleaned_inspection/idus_all_cleaned1.csv", index=False)