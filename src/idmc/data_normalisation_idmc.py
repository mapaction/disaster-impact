import pandas as pd
import json
import os

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.utils.azure_blob_utils import read_blob_to_json

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    IDMC_MAPPING
)

def main():
    blob_name = "disaster-impact/raw/idmc_idu/idus_all.json"
    SCHEMA_PATH_IDMC = "./src/idmc/idmc_schema.json"
    
    try:
        data = read_blob_to_json(blob_name)
    except Exception as e:
        print(f"Failed to load JSON data from blob: {e}")
        exit(1)
    
    idmc_df_raw = pd.json_normalize(data)
    idmc_df_raw = idmc_df_raw.apply(
        lambda row: row.map(lambda x: x.replace(";", "-") if isinstance(x, str) else x), axis=1
    )

    with open(SCHEMA_PATH_IDMC, "r") as schema_idmc:
        idmc_schema = json.load(schema_idmc)

    cleaned1_df = map_and_drop_columns(idmc_df_raw, IDMC_MAPPING)
    cleaned2_df = change_data_type(cleaned1_df, idmc_schema)
    cleaned2_df['Date'] = pd.to_datetime(cleaned2_df['Date'], errors='coerce')

    os.makedirs("./data_mid_1/idmc_idu", exist_ok=True)
    output_file_path = "./data_mid_1/idmc_idu/idus_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)

    print(f"Cleaned IDMC data saved for inspection at: {output_file_path}")

if __name__ == "__main__":
    main()
