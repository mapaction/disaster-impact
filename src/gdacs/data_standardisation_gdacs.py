import pandas as pd
import numpy as np
import json
import os
from jsonschema import validate, ValidationError
from datetime import datetime

from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GDACS_MAPPING

GDACS_INPUT_CSV = "./data/gdacs_all_types_yearly_v2_fast/combined_gdacs_data.csv"
SCHEMA_PATH = "./src/gdacs/schema.json"
OUTPUT_DIR = "./data_mid/gdacs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "gdacs_standardized_phase1.csv")

with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

gdacs_df = pd.read_csv(GDACS_INPUT_CSV)

standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)

for standard_col, source_col in GDACS_MAPPING.items():
    if source_col and source_col in gdacs_df.columns:
        standard_df[standard_col] = gdacs_df[source_col]
    else:
        standard_df[standard_col] = np.nan

if 'Source_Event_IDs' in standard_df.columns:
    standard_df['Source_Event_IDs'] = standard_df['Source_Event_IDs'].apply(
        lambda x: [str(x)] if pd.notnull(x) else []
    )

if 'Location' in standard_df.columns:
    standard_df['Location'] = standard_df['Location'].apply(
        lambda x: [x] if pd.notnull(x) else []
    )

if 'Latitude' in standard_df.columns:
    standard_df['Latitude'] = standard_df['Latitude'].apply(
        lambda x: [float(x)] if pd.notnull(x) else []
    )

if 'Longitude' in standard_df.columns:
    standard_df['Longitude'] = standard_df['Longitude'].apply(
        lambda x: [float(x)] if pd.notnull(x) else []
    )

if 'External_Links' in standard_df.columns:
    standard_df['External_Links'] = [[] for _ in range(len(standard_df))]

if 'Comments' in standard_df.columns:
    standard_df['Comments'] = standard_df['Comments'].apply(
        lambda x: [x] if pd.notnull(x) else []
    )

if 'Source' in standard_df.columns:
    standard_df['Source'] = standard_df['Source'].apply(
        lambda x: [x] if pd.notnull(x) else []
    )

if 'Date' in standard_df.columns:
    standard_df['Date'] = pd.to_datetime(standard_df['Date'], errors='coerce')
    standard_df['Year'] = standard_df['Date'].dt.year
    standard_df['Month'] = standard_df['Date'].dt.month
    standard_df['Day'] = standard_df['Date'].dt.day
    standard_df['Time'] = standard_df['Date'].dt.time.astype(str)
    standard_df['Date'] = standard_df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S')

if 'Severity' in standard_df.columns:
    standard_df['Severity'] = standard_df['Severity'].apply(
        lambda x: str(x) if pd.notnull(x) else None
    )

if 'Population_Affected' in standard_df.columns:
    standard_df['Population_Affected'] = standard_df['Population_Affected'].apply(
        lambda x: int(x) if pd.notnull(x) else None
    )

# Convert Year, Month, Day from float to int or None
for col in ['Year', 'Month', 'Day']:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(lambda x: int(x) if pd.notnull(x) else None)

# Replace NaN with None for JSON schema validation
standard_df = standard_df.where(pd.notnull(standard_df), None)

for i, record in standard_df.iterrows():
    record_dict = record.to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

for col in ['Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'Source', 'Comments', 'External_Links']:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(str)

final_df = standard_df.replace({None: ''})

final_df.to_csv(OUTPUT_CSV, index=False)

print(f"Standardization complete. Output written to {OUTPUT_CSV}")
