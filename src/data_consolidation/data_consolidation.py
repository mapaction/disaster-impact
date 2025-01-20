import pandas as pd
import json

from src.data_consolidation.dictionary import STANDARD_COLUMNS

UNIFIED_SCHEMA_PATH = "./src/unified/unified_schema.json"

df_glide_mid = pd.read_csv('./data_mid/glide/cleaned_inspaction/cleaned_glide.csv')
df_gdacs_mid = pd.read_csv('./data_mid/gdacs/cleaned_inspaction/cleaned_gdacs.csv')
df_disaster_charter_mid = pd.read_csv('./data_mid/disaster_charter/cleaned_inspection/disaster_charter_cleaned.csv')
df_emdat_mid = pd.read_csv('./data_mid/emdat/cleaned_inspection/emdat_cleaned.csv')
df_idmc_mid = pd.read_csv('./data_mid/idmc_idu/cleaned_inspection/idus_all_cleaned1.csv')
df_cerf_mid = pd.read_csv('./data_mid/cerf/cleaned_inspection/cleaned_cerf.csv')
df_ifrc_mid = pd.read_csv('./data_mid/ifrc_eme/cleaned_inspection/cleaned_ifrc_eme.csv')

with open(UNIFIED_SCHEMA_PATH, 'r') as f:
    schema = json.load(f)
