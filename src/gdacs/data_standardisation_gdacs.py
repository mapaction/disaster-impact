import pandas as pd
import numpy as np
import json
import os
from jsonschema import validate, ValidationError
import re
import pycountry

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

# Attempt to extract Country from Event_Name only if pattern "in <Country>" is present and Country is NaN
if 'Country' in standard_df.columns and 'Event_Name' in standard_df.columns:
    def extract_country_from_event_name(row):
        if pd.isna(row['Country']) and isinstance(row['Event_Name'], str):
            # Regex to find "in <Country>" at the end of the event name
            match = re.search(r'\bin\s+([A-Za-z0-9\s\(\)-]+)$', row['Event_Name'])
            if match:
                return match.group(1).strip()
        return row['Country']

    standard_df['Country'] = standard_df.apply(extract_country_from_event_name, axis=1)

# Extract ISO3 code from Country column and place into Country_Code
if 'Country' in standard_df.columns:
    # Extract code inside parentheses if present
    standard_df['Country_Code'] = standard_df['Country'].str.extract(r'\(([^)]*)\)')
    # Remove the parentheses and code from the Country field
    standard_df['Country'] = standard_df['Country'].str.replace(r'\s*\([^)]*\)$', '', regex=True)

# Now fill missing Country_Code using pycountry if Country is available
def get_iso3_from_country_name(country_name):
    if country_name and isinstance(country_name, str):
        try:
            matches = pycountry.countries.search_fuzzy(country_name)
            if matches:
                return matches[0].alpha_3
        except LookupError:
            return None
    return None

if 'Country' in standard_df.columns and 'Country_Code' in standard_df.columns:
    # Only fill in if Country_Code is None and Country is not None
    standard_df['Country_Code'] = standard_df.apply(
        lambda row: row['Country_Code'] if row['Country_Code'] is not None else get_iso3_from_country_name(row['Country']),
        axis=1
    )

if 'Source_Event_IDs' in standard_df.columns:
    standard_df['Source_Event_IDs'] = standard_df['Source_Event_IDs'].apply(
        lambda x: [str(x)] if pd.notna(x) else []
    )

if 'Location' in standard_df.columns:
    standard_df['Location'] = standard_df['Location'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

if 'Latitude' in standard_df.columns:
    standard_df['Latitude'] = standard_df['Latitude'].apply(
        lambda x: [float(x)] if pd.notna(x) else []
    )

if 'Longitude' in standard_df.columns:
    standard_df['Longitude'] = standard_df['Longitude'].apply(
        lambda x: [float(x)] if pd.notna(x) else []
    )

if 'External_Links' in standard_df.columns:
    standard_df['External_Links'] = [[] for _ in range(len(standard_df))]

if 'Comments' in standard_df.columns:
    standard_df['Comments'] = standard_df['Comments'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

if 'Source' in standard_df.columns:
    standard_df['Source'] = standard_df['Source'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

if 'Date' in standard_df.columns:
    standard_df['Date'] = pd.to_datetime(standard_df['Date'], errors='coerce')
    standard_df['Year'] = standard_df['Date'].dt.year
    standard_df['Month'] = standard_df['Date'].dt.month
    standard_df['Day'] = standard_df['Date'].dt.day
    standard_df['Time'] = standard_df['Date'].dt.strftime('%H:%M:%S')
    standard_df['Date'] = standard_df['Date'].dt.strftime('%Y-%m-%d')

if 'Severity' in standard_df.columns:
    standard_df['Severity'] = standard_df['Severity'].apply(
        lambda x: str(x) if pd.notna(x) else None
    )

if 'Population_Affected' in standard_df.columns:
    standard_df['Population_Affected'] = standard_df['Population_Affected'].apply(
        lambda x: int(x) if pd.notna(x) else None
    )

for col in ['Year', 'Month', 'Day']:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(lambda x: int(x) if pd.notna(x) else None)

if 'Time' in standard_df.columns:
    standard_df['Time'] = standard_df['Time'].where(pd.notna(standard_df['Time']), None)

standard_df = standard_df.astype(object).where(pd.notnull(standard_df), None)

for i, record in standard_df.iterrows():
    record_dict = record.to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

array_fields = ['Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'Source', 'Comments', 'External_Links']
for col in array_fields:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(lambda arr: json.dumps(arr) if arr is not None else '[]')

standard_df.to_csv(OUTPUT_CSV, index=False)

print(f"Standardization complete. Output written to {OUTPUT_CSV}")
