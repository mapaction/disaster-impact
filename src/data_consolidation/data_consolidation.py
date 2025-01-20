import pandas as pd
import json

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

schema_properties = schema['properties']

def ensure_columns_exist(df, schema_properties):
    for column, attributes in schema_properties.items():
        if column not in df.columns:
            if "array" in attributes["type"]:
                df[column] = pd.Series([[] for _ in range(len(df))])
            elif "integer" in attributes["type"]:
                df[column] = pd.NA
            elif "number" in attributes["type"]:
                df[column] = pd.NA
            elif "string" in attributes["type"]:
                df[column] = None
            else:
                df[column] = None
        else:
            # Cast existing column to the appropriate type if needed
            if "array" in attributes["type"]:
                df[column] = df[column].apply(lambda x: x if isinstance(x, list) else [])
            elif "integer" in attributes["type"]:
                df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
            elif "number" in attributes["type"]:
                df[column] = pd.to_numeric(df[column], errors='coerce')
            elif "string" in attributes["type"]:
                df[column] = df[column].astype(str).replace('nan', None)
    return df

dataframes_step_2 = {}
for name, df in dataframes.items():
    dataframes_step_2[name] = ensure_columns_exist(df, schema_properties)

for name, df in dataframes_step_2.items():
    print(f"Columns in {name} DataFrame after schema update:")
    print(df.columns.tolist())
    print("\n")
