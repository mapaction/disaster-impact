import pandas as pd
import json
import os

from src.data_consolidation.dictionary import STANDARD_COLUMNS

os.makedirs('./data_mid/data_standardised', exist_ok=True)

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

def get_default_value(data_type):
    if data_type == "string":
        return None
    elif data_type == "array":
        return []
    elif data_type == "integer":
        return None
    elif data_type == "number":
        return None
    else:
        return None
    
def ensure_columns(df, standard_columns, schema_properties):
    for column in standard_columns:
        if column not in df.columns:
            data_type = schema_properties.get(column, {}).get("type", ["string"])[0]
            default_value = get_default_value(data_type)
            
            df[column] = [default_value] * len(df)
    
    df = df[standard_columns]
    return df

standardised_dataframes = {}
for name, df in dataframes.items():
    standardised_dataframes[name] = ensure_columns(df, STANDARD_COLUMNS, schema_properties)

for name, df in standardised_dataframes.items():
    output_path = f'./data_mid/data_standardised/{name}_standardised.csv'
    df.to_csv(output_path, index=False)
