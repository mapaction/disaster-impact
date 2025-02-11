import pandas as pd
import json
import os
import pycountry

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.utils.azure_blob_utils import read_blob_to_dataframe
from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    CERF_MAPPING,
)

def main():
    blob_name = "disaster-impact/raw/cerf/cerf_emergency_data_dynamic_web_scrape.csv"
    SCHEMA_PATH_CERF = "./src/cerf/cerf_schema.json"

    try:
        cerf_df_raw = read_blob_to_dataframe(blob_name)
    except Exception as e:
        print(f"Failed to load CSV data from blob: {e}")
        exit(1)

    with open(SCHEMA_PATH_CERF, "r") as schema_cerf:
        cerf_schema = json.load(schema_cerf)

    cleaned1_df = map_and_drop_columns(cerf_df_raw, CERF_MAPPING)

    def get_iso3_code(country_name):
        try:
            return pycountry.countries.lookup(country_name).alpha_3
        except LookupError:
            return None

    cleaned1_df['Country_Code'] = cleaned1_df['Country'].apply(get_iso3_code)
    cleaned2_df = change_data_type(cleaned1_df, cerf_schema)

    # Reorder of schema columns
    schema_order = list(cerf_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]
    #

    os.makedirs("./data_mid_1/cerf/", exist_ok=True)
    output_file_path = "./data_mid_1/cerf/cerf_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)

    print(f"Cleaned CERF data saved for inspection at: {output_file_path}")

if __name__ == "__main__":
    main()
