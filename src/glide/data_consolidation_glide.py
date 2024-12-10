import pandas as pd
import ast
import hashlib
import numpy as np
import os
import json
from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GLIDE_MAPPING

# Paths
SCHEMA_PATH = "/home/evangelos/src/disaster-impact/src/glide/schema.json"
STANDARDIZED_CSV = "./data_mid/glide/glide_standardized_phase1.csv"
os.makedirs("./data_out/glide", exist_ok=True)

# Load schema (optional, for future validation)
with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)
OUTPUT_CSV = "./data_out/glide/glide_consolidated.csv"
ARRAY_FIELDS = ['Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'External_Links', 'Comments', 'Source']
GROUP_KEY = ['Event_Type', 'Country', 'Country_Code', 'Date']

df = pd.read_csv(STANDARDIZED_CSV)

# Function to parse Python-style list strings
def parse_list_string(s):
    if pd.isnull(s) or s.strip() == '':
        return []
    try:
        return ast.literal_eval(s)  # Safely evaluate Python literals
    except (ValueError, SyntaxError):
        print(f"Error parsing list: {s}")
        return []

# Apply the parsing function to the specified fields
ARRAY_FIELDS = ['Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'External_Links', 'Comments', 'Source']
for field in ARRAY_FIELDS:
    if field in df.columns:
        df[field] = df[field].apply(parse_list_string)

def consolidate_group(group):
    consolidated = {}

    # First, handle array fields: combine them from all rows, remove duplicates
    for field in ARRAY_FIELDS:
        combined = set()
        for arr in group[field]:
            combined.update(arr)
        consolidated[field] = list(combined)

    # For single-value fields: pick the first non-null value
    SINGLE_VALUE_FIELDS = [
        'Event_ID', 'Event_Name', 'Year', 'Month', 'Day', 'Time', 'Severity',
        'Population_Affected', 'Fatalities', 'People_Displaced', 'Financial_Loss',
        'Alert_Level'
    ] + GROUP_KEY  # Include GROUP_KEY fields as they define the group

    for field in SINGLE_VALUE_FIELDS:
        vals = group[field].dropna()
        consolidated[field] = vals.iloc[0] if len(vals) > 0 else np.nan

    # Generate a unique Event_ID from Source_Event_IDs
    source_ids = sorted(consolidated['Source_Event_IDs'])
    unique_str = "|".join(source_ids)
    event_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
    consolidated['Event_ID'] = event_id

    # # Convert arrays back to JSON strings if you want to keep them in a standard format
    # for field in ARRAY_FIELDS:
    #     consolidated[field] = json.dumps(consolidated[field])

    return pd.Series(consolidated)

# Group by the uniqueness key and consolidate
consolidated_df = df.groupby(GROUP_KEY).apply(consolidate_group).reset_index(drop=True)

# Create a new DataFrame with enriched standard columns
standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)
for col in ENRICHED_STANDARD_COLUMNS:
    if col in consolidated_df.columns:
        standard_df[col] = consolidated_df[col]
    else:
        standard_df[col] = np.nan  # Add missing columns with NaN values

# Save the final DataFrame to CSV
standard_df.to_csv(OUTPUT_CSV, index=False)
print(f"Consolidation complete. Output written to {OUTPUT_CSV}")
