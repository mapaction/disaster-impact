import pandas as pd
import ast
import hashlib
import numpy as np
import os
import json
from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GDACS_MAPPING

SCHEMA_PATH = "./src/gdacs/schema.json"
STANDARDIZED_CSV = "./data_mid/gdacs_v3/gdacs_standardized_phase1.csv"
os.makedirs("./data_out/gdacs", exist_ok=True)

with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)
OUTPUT_CSV = "./data_out/gdacs/gdacs_consolidated.csv"
ARRAY_FIELDS = ['Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'External_Links', 'Comments', 'Source', 'Severity', 'Alert_Level']
GROUP_KEY = ['Event_Type', 'Country', 'Date']

df = pd.read_csv(STANDARDIZED_CSV)

def parse_list_string(s):
    if pd.isnull(s) or s.strip() == '':
        return []
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        print(f"Error parsing list: {s}")
        return []

for field in ARRAY_FIELDS:
    if field in df.columns:
        df[field] = df[field].apply(parse_list_string)

def consolidate_group(group):
    consolidated = {}
    for field in ARRAY_FIELDS:
        combined = set()
        for arr in group[field]:
            combined.update(arr)
        consolidated[field] = list(combined)

    SINGLE_VALUE_FIELDS = [
        'Event_ID', 'Event_Name', 'Country_Code' ,'Year', 'Month', 'Day', 'Time',
        'Population_Affected', 'Fatalities', 'People_Displaced', 'Financial_Loss'
    ] + GROUP_KEY

    for field in SINGLE_VALUE_FIELDS:
        if field in group.columns:
            vals = group[field].dropna()
            consolidated[field] = vals.iloc[0] if len(vals) > 0 else np.nan
        else:
            consolidated[field] = np.nan

    source_ids = sorted(consolidated['Source_Event_IDs'])
    unique_str = "|".join(source_ids)
    event_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest() if source_ids else None
    consolidated['Event_ID'] = event_id

    return pd.Series(consolidated)

consolidated_df = df.groupby(GROUP_KEY).apply(consolidate_group).reset_index(drop=True)

standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)
for col in ENRICHED_STANDARD_COLUMNS:
    if col in consolidated_df.columns:
        standard_df[col] = consolidated_df[col]
    else:
        standard_df[col] = np.nan

standard_df.to_csv(OUTPUT_CSV, index=False)
print(f"Consolidation complete. Output written to {OUTPUT_CSV}")
