import pandas as pd
import numpy as np
import json
import os
from jsonschema import validate, ValidationError
from datetime import datetime
from src.data_consolidation.v2.dictionary_v2 import (
    ENRICHED_STANDARD_COLUMNS, 
    DISASTER_CHARTER_MAPPING
)

DISASTER_CHARTER_INPUT_CSV = "/home/evangelos/src/disaster-impact/data/disaster-charter/disaster_activations_boosted_dec.csv"
SCHEMA_PATH = "/home/evangelos/src/disaster-impact/src/cgt/schema.json"
OUTPUT_DIR = "./data_mid/disaster_charter"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "disaster_charter_standardized_phase1.csv")

with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

dc_df = pd.read_csv(DISASTER_CHARTER_INPUT_CSV)
standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)

for standard_col, source_col in DISASTER_CHARTER_MAPPING.items():
    if source_col and source_col in dc_df.columns:
        standard_df[standard_col] = dc_df[source_col]
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
    standard_df['Latitude'] = [[] for _ in range(len(standard_df))]

if 'Longitude' in standard_df.columns:
    standard_df['Longitude'] = [[] for _ in range(len(standard_df))]

if 'External_Links' in standard_df.columns:
    standard_df['External_Links'] = standard_df['External_Links'].apply(
        lambda x: [x] if pd.notnull(x) else []
    )

for col in ['Comments', 'Source', 'Severity', 'Alert_Level']:
    if col in standard_df.columns:
        standard_df[col] = [[] for _ in range(len(standard_df))]

# Functions to extract Year, Month, and Day from the ISO 8601 Date
def parse_iso_date(date_str):
    if pd.isnull(date_str) or date_str.strip() == '':
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

def extract_year(date_str):
    dt = parse_iso_date(date_str)
    return dt.year if dt else None

def extract_month(date_str):
    dt = parse_iso_date(date_str)
    return dt.month if dt else None

def extract_day(date_str):
    dt = parse_iso_date(date_str)
    return dt.day if dt else None

# Derive Year, Month, and Day from Date
if 'Date' in standard_df.columns:
    standard_df['Year'] = standard_df['Date'].apply(extract_year)
    standard_df['Month'] = standard_df['Date'].apply(extract_month)
    standard_df['Day'] = standard_df['Date'].apply(extract_day)

for i, record in standard_df.iterrows():
    record_dict = record.replace({np.nan: None}).to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

final_df = standard_df.replace({np.nan: ''})
final_df.to_csv(OUTPUT_CSV, index=False)

print(f"Standardization complete. Output written to {OUTPUT_CSV}")
