"""Cerf data normalisation script."""

import json
from pathlib import Path

import pandas as pd
import pycountry

from src.data_consolidation.dictionary import (
    CERF_MAPPING,
)
from src.glide.data_normalisation_glide import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)
from src.utils.azure_blob_utils import read_blob_to_dataframe

SCHEMA_PATH_CERF = "./src/cerf/cerf_schema.json"
EVENT_CODE_CSV = "./static_data/event_code_table.csv"


def main() -> None:
    """Normalise CERF data."""
    blob_name = "disaster-impact/raw/cerf/cerf_emergency_data_dynamic_web_scrape.csv"
    cerf_df_raw = read_blob_to_dataframe(blob_name)

    with Path(SCHEMA_PATH_CERF).open() as schema_cerf:
        cerf_schema = json.load(schema_cerf)

    cleaned1_df = map_and_drop_columns(cerf_df_raw, CERF_MAPPING)

    def get_iso3_code(country_name: str) -> None:
        try:
            return pycountry.countries.lookup(country_name).alpha_3
        except LookupError:
            return None

    cleaned1_df["Country_Code"] = cleaned1_df["Country"].apply(get_iso3_code)
    cleaned2_df = change_data_type(cleaned1_df, cerf_schema)
    cleaned2_df["Date"] = pd.to_datetime(cleaned2_df["Date"], errors="coerce")
    cleaned2_df = normalize_event_type(cleaned2_df, EVENT_CODE_CSV)
    schema_order = list(cerf_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]
    Path("./data_mid_1/cerf/").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/cerf/cerf_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
