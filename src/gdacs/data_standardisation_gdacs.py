import pandas as pd
import numpy as np
import json
import os
from jsonschema import validate, ValidationError
import re
import pycountry

from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GDACS_MAPPING

GDACS_INPUT_CSV = "./data/gdacs_all_types_yearly_v3_fast/combined_gdacs_data.csv"
SCHEMA_PATH = "./src/gdacs/schema.json"
OUTPUT_DIR = "./data_mid/gdacs_v3"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "gdacs_standardized_phase1.csv")

with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

gdacs_df = pd.read_csv(GDACS_INPUT_CSV)

# 1) If 'coordinates' is a string representation like "[167.418, -14.9439]",
#    parse it into a Python list before doing any mapping.
if 'coordinates' in gdacs_df.columns:
    def parse_coordinates(x):
        """
        Safely parse a string like '[167.418, -14.9439]' into a Python list [167.418, -14.9439].
        If parsing fails or x is not a valid string, return None.
        """
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return None
        # If it's already a list/array, just return as-is
        return x

    gdacs_df['coordinates'] = gdacs_df['coordinates'].apply(parse_coordinates)

# 2) Create a new DataFrame with the columns you want
standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)

# 3) Copy or initialize columns based on GDACS_MAPPING
for standard_col, source_col in GDACS_MAPPING.items():
    if source_col and source_col in gdacs_df.columns:
        standard_df[standard_col] = gdacs_df[source_col]
    else:
        standard_df[standard_col] = np.nan

# 4) We now extract actual Latitude/Longitude from 'coordinates' into the correct columns
#    only if those columns exist in standard_df.
#    NOTE: We do it after the initial assignment because GDACS_MAPPING for
#    'Latitude'/'Longitude' points to the same 'coordinates' column.
if 'Latitude' in standard_df.columns:
    # The column currently has the same data as 'coordinates' (a list),
    # we must pick element [1] as latitude.
    def extract_lat(coords):
        # coords should be a list [lon, lat], so coords[1] is lat
        if isinstance(coords, list) and len(coords) == 2:
            return coords[1]
        return None

    standard_df['Latitude'] = standard_df['Latitude'].apply(extract_lat)

if 'Longitude' in standard_df.columns:
    # Similarly, pick element [0] as longitude
    def extract_lon(coords):
        # coords should be a list [lon, lat], so coords[0] is lon
        if isinstance(coords, list) and len(coords) == 2:
            return coords[0]
        return None

    standard_df['Longitude'] = standard_df['Longitude'].apply(extract_lon)

# 5) Attempt to extract Country from Event_Name only if pattern "in <Country>" is present and Country is NaN
if 'Country' in standard_df.columns and 'Event_Name' in standard_df.columns:
    def extract_country_from_event_name(row):
        if pd.isna(row['Country']) and isinstance(row['Event_Name'], str):
            match = re.search(r'\bin\s+([A-Za-z0-9\s\(\)-]+)$', row['Event_Name'])
            if match:
                return match.group(1).strip()
        return row['Country']

    standard_df['Country'] = standard_df.apply(extract_country_from_event_name, axis=1)

# 6) Extract ISO3 code from Country column into Country_Code (parsing parentheses)
if 'Country' in standard_df.columns:
    # Extract code inside parentheses if present
    standard_df['Country_Code'] = standard_df['Country'].str.extract(r'\(([^)]*)\)')
    # Remove the parentheses and code from the Country field
    standard_df['Country'] = standard_df['Country'].str.replace(r'\s*\([^)]*\)$', '', regex=True)

# 7) Now fill missing Country_Code using pycountry if Country is available
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
    standard_df['Country_Code'] = standard_df.apply(
        lambda row: row['Country_Code'] if row['Country_Code'] is not None 
                                         else get_iso3_from_country_name(row['Country']),
        axis=1
    )

# 8) Convert Source_Event_IDs to array of strings
if 'Source_Event_IDs' in standard_df.columns:
    standard_df['Source_Event_IDs'] = standard_df['Source_Event_IDs'].apply(
        lambda x: [str(x)] if pd.notna(x) else []
    )

# 9) Convert Location to array of strings (if it exists)
if 'Location' in standard_df.columns:
    standard_df['Location'] = standard_df['Location'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# 10) Convert the numeric lat/lon to a single-element array of floats
if 'Latitude' in standard_df.columns:
    standard_df['Latitude'] = standard_df['Latitude'].apply(
        lambda val: [float(val)] if pd.notna(val) else []
    )

if 'Longitude' in standard_df.columns:
    standard_df['Longitude'] = standard_df['Longitude'].apply(
        lambda val: [float(val)] if pd.notna(val) else []
    )

# 11) External_Links array
if 'External_Links' in standard_df.columns:
    standard_df['External_Links'] = [[] for _ in range(len(standard_df))]

# 12) Comments array
if 'Comments' in standard_df.columns:
    standard_df['Comments'] = standard_df['Comments'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# 13) Source array
if 'Source' in standard_df.columns:
    # If you want to hardcode Source to ["GDACS"] for all rows:
    # standard_df['Source'] = [["GDACS"]] * len(standard_df)
    # Or just convert existing data to an array:
    standard_df['Source'] = standard_df['Source'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# 14) Date/Year/Month/Day/Time
if 'Date' in standard_df.columns:
    standard_df['Date'] = pd.to_datetime(standard_df['Date'], errors='coerce')
    standard_df['Year'] = standard_df['Date'].dt.year
    standard_df['Month'] = standard_df['Date'].dt.month
    standard_df['Day'] = standard_df['Date'].dt.day
    standard_df['Time'] = standard_df['Date'].dt.strftime('%H:%M:%S')
    # If you prefer a full ISO 8601 date-time, do this instead:
    # standard_df['Date'] = standard_df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    # Otherwise just keep the YYYY-MM-DD format
    standard_df['Date'] = standard_df['Date'].dt.strftime('%Y-%m-%d')

# 15) Severity as array of strings
if 'Severity' in standard_df.columns:
    standard_df['Severity'] = standard_df['Severity'].apply(
        lambda x: [str(x)] if pd.notna(x) else []
    )

# 16) Alert_Level as array of strings
if 'Alert_Level' in standard_df.columns:
    standard_df['Alert_Level'] = standard_df['Alert_Level'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# 17) Convert population to int
if 'Population_Affected' in standard_df.columns:
    standard_df['Population_Affected'] = standard_df['Population_Affected'].apply(
        lambda x: int(x) if pd.notna(x) else None
    )

# 18) Convert Year/Month/Day to int
for col in ['Year', 'Month', 'Day']:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(lambda x: int(x) if pd.notna(x) else None)

# 19) Fix Time if empty
if 'Time' in standard_df.columns:
    standard_df['Time'] = standard_df['Time'].where(pd.notna(standard_df['Time']), None)

# 20) Replace any remaining NaN with None
standard_df = standard_df.astype(object).where(pd.notnull(standard_df), None)

# 21) Validate against JSON schema
for i, record in standard_df.iterrows():
    record_dict = record.to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

# 22) (Optional) If you need to store array columns as JSON strings in your final CSV:
# array_fields = [
#     'Source_Event_IDs', 'Location', 'Latitude', 'Longitude', 'Source',
#     'Comments', 'External_Links', 'Severity', 'Alert_Level'
# ]
# for col in array_fields:
#     standard_df[col] = standard_df[col].apply(
#         lambda arr: json.dumps(arr) if arr is not None else '[]'
# )

# 23) Replace leftover NaN with empty string for CSV output
standard_df = standard_df.replace({np.nan: ''})

# 24) Write out the standardized CSV
standard_df.to_csv(OUTPUT_CSV, index=False)

print(f"Standardization complete. Output written to {OUTPUT_CSV}")
