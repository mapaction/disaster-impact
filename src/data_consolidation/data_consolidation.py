import pandas as pd
import json
import os

from src.data_consolidation.dictionary import STANDARD_COLUMNS

UNIFIED_SCHEMA_PATH = "./src/unified/json_schemas/unified_schema.json"

dataframes = {
    "glide": pd.read_csv('./data_mid/glide/cleaned_inspaction/cleaned_glide.csv'),
    "gdacs": pd.read_csv('./data_mid/gdacs/cleaned_inspaction/cleaned_gdacs.csv'),
    "disaster_charter": pd.read_csv('./data_mid/disaster_charter/cleaned_inspection/disaster_charter_cleaned.csv'),
    "emdat": pd.read_csv('./data_mid/emdat/cleaned_inspection/emdat_cleaned.csv'),
    "idmc": pd.read_csv('./data_mid/idmc_idu/cleaned_inspection/idus_all_cleaned1.csv'),
    "cerf": pd.read_csv('./data_mid/cerf/cleaned_inspection/cleaned_cerf.csv'),
    "ifrc": pd.read_csv('./data_mid/ifrc_eme/cleaned_inspection/cleaned_ifrc_eme.csv')
}

with open(UNIFIED_SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

schema_properties = schema["properties"]