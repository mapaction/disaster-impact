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

def ensure_columns_exist_and_order(df, schema_props):
    """
    Ensure all columns from the schema exist in the DataFrame in the correct order.
    If a column is missing, add it with the appropriate type.
    """
    all_columns = list(schema_props.keys())
    for column in all_columns:
        if column not in df.columns:
            if "array" in schema_props[column]["type"]:
                df[column] = pd.Series([[] for _ in range(len(df))])
            elif "integer" in schema_props[column]["type"]:
                df[column] = pd.NA
            elif "number" in schema_props[column]["type"]:
                df[column] = pd.NA
            elif "string" in schema_props[column]["type"]:
                df[column] = None
            else:
                df[column] = None
        else:
            # Cast existing column to the appropriate type if needed
            if "array" in schema_props[column]["type"]:
                df[column] = df[column].apply(lambda x: x if isinstance(x, list) else [])
            elif "integer" in schema_props[column]["type"]:
                df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
            elif "number" in schema_props[column]["type"]:
                df[column] = pd.to_numeric(df[column], errors='coerce')
            elif "string" in schema_props[column]["type"]:
                df[column] = df[column].astype(str).replace('nan', None)

    # Reorder columns to match schema
    df = df[all_columns]
    return df

dataframes_step_2 = {}
for name, df in dataframes.items():
    dataframes_step_2[name] = ensure_columns_exist_and_order(df, schema_properties)

output_dir = './data_mid/cleaned_inspection_2'
os.makedirs(output_dir, exist_ok=True)

for name, df in dataframes_step_2.items():
    output_path = f"{output_dir}/{name}_cleaned.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {name} DataFrame to {output_path}")
