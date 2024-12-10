import pandas as pd
import numpy as np
import json
import os
from jsonschema import validate, ValidationError

from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GLIDE_MAPPING

GLIDE_INPUT_CSV = "/home/evangelos/src/disaster-impact/data/glide/glide_data_combined_all.csv"
SCHEMA_PATH = "/home/evangelos/src/disaster-impact/src/glide/schema.json"
os.makedirs("./data_mid/glide", exist_ok=True)
OUTPUT_CSV = "./data_mid/glide/glide_standardized_phase1.csv"

# Step 1: Load schema for validation
with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

# Step 2: Read the original GLIDE data
glide_df = pd.read_csv(GLIDE_INPUT_CSV)

# Step 3: Create a new DataFrame with the enriched standard columns
standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)

# Step 4: Apply GLIDE_MAPPING
for standard_col, source_col in GLIDE_MAPPING.items():
    if source_col and source_col in glide_df.columns:
        standard_df[standard_col] = glide_df[source_col]
    else:
        standard_df[standard_col] = np.nan

# Step 5: Convert certain fields to arrays if they have single values
# For Source_Event_IDs, if we have a single source ID, we wrap it in a list
if 'Source_Event_IDs' in standard_df.columns:
    standard_df['Source_Event_IDs'] = standard_df['Source_Event_IDs'].apply(
        lambda x: [x] if pd.notnull(x) else []
    )

# Location, Latitude, Longitude, External_Links should also be arrays
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

# Step 6: Validate against schema
for i, record in standard_df.iterrows():
    # Convert the row to a dict with None instead of NaN
    record_dict = record.replace({np.nan: None}).to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

# Step 7: Write out the standardized DataFrame to CSV
# Replace NaN with empty strings for cleaner CSV output
final_df = standard_df.replace({np.nan: ''})
final_df.to_csv(OUTPUT_CSV, index=False)

print(f"Standardization complete. Output written to {OUTPUT_CSV}")
