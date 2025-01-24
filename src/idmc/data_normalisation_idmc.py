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

IDMC_INPUT_JSON = "/home/evangelos/src/disaster-impact/data/idmc_idu/idus_all.json"
SCHEMA_PATH_IDMC = "./src/idmc/idmc_schema.json"

with open(IDMC_INPUT_JSON, "r") as file:
    data = json.load(file)

idmc_df_raw = pd.json_normalize(data)

idmc_df_raw = idmc_df_raw.apply(
    lambda row: row.map(lambda x: x.replace(";", "-") if isinstance(x, str) else x), axis=1
)

with open(SCHEMA_PATH_IDMC, "r") as schema_idmc:
    idmc_schema = json.load(schema_idmc)

cleaned1_df = map_and_drop_columns(idmc_df_raw, IDMC_MAPPING)

cleaned2_df = change_data_type(cleaned1_df, idmc_schema)

os.makedirs("./data_mid/idmc_idu/cleaned_inspection", exist_ok=True)

output_file_path = "./data_mid/idmc_idu/cleaned_inspection/idus_all_cleaned1.csv"
cleaned2_df.to_csv(output_file_path, index=False)

print(f"Cleaned IDMC data saved for inspection at: {output_file_path}")
