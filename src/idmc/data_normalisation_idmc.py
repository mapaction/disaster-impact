"""IDMC data normalisation script."""

import json
import logging
import sys
from pathlib import Path

import pandas as pd

from src.data_consolidation.dictionary import IDMC_MAPPING
from src.utils.azure_blob_utils import read_blob_to_json
from src.utils.util import (
    change_data_type,
    map_and_drop_columns,
    normalize_event_type,
)

SCHEMA_PATH_IDMC = "./src/idmc/idmc_schema.json"
EVENT_CODE_CSV = "./static_data/event_code_table.csv"


def main() -> None:
    """Normalise IDMC data and save to CSV file."""
    blob_name = "disaster-impact/raw/idmc_idu/idus_all.json"

    try:
        data = read_blob_to_json(blob_name)
    except Exception as e:
        error_message = f"Error reading blob: {e}"
        logging.exception(error_message)
        sys.exit()

    idmc_df_raw = pd.json_normalize(data)
    idmc_df_raw = idmc_df_raw.apply(
        lambda row: row.map(
            lambda x: x.replace(";", "-") if isinstance(x, str) else x,
        ),
        axis=1,
    )

    with Path(SCHEMA_PATH_IDMC).open() as schema_idmc:
        idmc_schema = json.load(schema_idmc)

    cleaned1_df = map_and_drop_columns(idmc_df_raw, IDMC_MAPPING)
    cleaned2_df = change_data_type(cleaned1_df, idmc_schema)
    cleaned2_df["Date"] = pd.to_datetime(cleaned2_df["Date"], errors="coerce")
    cleaned2_df = normalize_event_type(cleaned2_df, EVENT_CODE_CSV)
    schema_order = list(idmc_schema["properties"].keys())
    ordered_columns = [col for col in schema_order if col in cleaned2_df.columns]
    remaining_columns = [col for col in cleaned2_df.columns if col not in schema_order]
    final_columns_order = ordered_columns + remaining_columns
    cleaned2_df = cleaned2_df[final_columns_order]

    Path("./data_mid_1/idmc_idu").mkdir(parents=True, exist_ok=True)
    output_file_path = "./data_mid_1/idmc_idu/idus_mid1.csv"
    cleaned2_df.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
