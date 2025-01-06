import pandas as pd
import numpy as np
import json
import os
import re
import pycountry
from jsonschema import validate, ValidationError
import ast

from src.data_consolidation.v2.dictionary_v2 import ENRICHED_STANDARD_COLUMNS, GDACS_MAPPING

GDACS_INPUT_CSV = "./data/gdacs_all_types_yearly_v3_fast/combined_gdacs_data.csv"
SCHEMA_PATH = "./src/gdacs/schema.json"
OUTPUT_DIR = "./data_mid/gdacs_v3"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "gdacs_standardized_phase1.csv")

with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

gdacs_df = pd.read_csv(GDACS_INPUT_CSV)

# --- 1) PARSE "coordinates" COLUMN INTO LISTS ---
if 'coordinates' in gdacs_df.columns:
    def parse_coordinates(x):
        """
        Safely parse a string like "[167.418, -14.9439]" into [167.418, -14.9439].
        If parsing fails or x is not a valid string, return None.
        """
        if isinstance(x, str):
            try:
                return json.loads(x)  # or ast.literal_eval(x) if it's Python syntax
            except (json.JSONDecodeError, ValueError, SyntaxError):
                return None
        return x  # Already a list or NaN

    gdacs_df['coordinates'] = gdacs_df['coordinates'].apply(parse_coordinates)

# --- 2) PARSE "location" COLUMN INTO LISTS ---
if 'location' in gdacs_df.columns:
    def parse_location(x):
        """
        Handle values like "['United States']" so we end up with a real Python list: ['United States'].
        If parsing fails or x is not valid, return None (we'll convert it to [] later).
        """
        if isinstance(x, str):
            try:
                return ast.literal_eval(x)
            except (ValueError, SyntaxError):
                return None
        return x  # Might already be a list or NaN

    gdacs_df['location'] = gdacs_df['location'].apply(parse_location)

    
    # if 'Country' in gdacs_df.columns:
    #     gdacs_df['location'] = gdacs_df.apply(
    #         lambda row: [row['Country']] 
    #                     if (pd.isna(row['location']) or row['location'] == []) 
    #                        and pd.notna(row['Country']) 
    #                     else row['location'],
    #         axis=1
    #     )

# --- 3) CREATE THE STANDARD_DF WITH DESIRED COLUMNS ---
standard_df = pd.DataFrame(columns=ENRICHED_STANDARD_COLUMNS)

# --- 4) COPY OR INIT COLUMNS BASED ON GDACS_MAPPING ---
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

# --- 6) EXTRACT COUNTRY FROM EVENT_NAME IF COUNTRY IS NaN AND EVENT_NAME HAS "in X" ---
if 'Country' in standard_df.columns and 'Event_Name' in standard_df.columns:
    def extract_country_from_event_name(row):
        if pd.isna(row['Country']) and isinstance(row['Event_Name'], str):
            match = re.search(r'\bin\s+([A-Za-z0-9\s\(\)-]+)$', row['Event_Name'])
            if match:
                return match.group(1).strip()
        return row['Country']

    standard_df['Country'] = standard_df.apply(extract_country_from_event_name, axis=1)

# --- 7) ONLY EXTRACT PARENTHESIS CODE IF COUNTRY_CODE IS STILL NULL ---
if 'Country' in standard_df.columns and 'Country_Code' in standard_df.columns:
    # We'll do this row-by-row
    def maybe_extract_country_code(row):
        if pd.isna(row['Country_Code']) and isinstance(row['Country'], str):
            # Try to parse parentheses from Country
            match = re.search(r'\(([^)]*)\)', row['Country'])
            if match:
                return match.group(1).strip()
        return row['Country_Code']

    standard_df['Country_Code'] = standard_df.apply(maybe_extract_country_code, axis=1)

    # Now remove the parentheses from the Country field if they exist
    # (But only if there's actually parentheses. Otherwise, we skip.)
    standard_df['Country'] = standard_df['Country'].str.replace(r'\s*\([^)]*\)$', '', regex=True)

# --- 8) FILL IN MISSING COUNTRY_CODE WITH PYCOUNTRY ---
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
        lambda row: row['Country_Code'] 
                    if pd.notna(row['Country_Code']) 
                    else get_iso3_from_country_name(row['Country']),
        axis=1
    )

# --- 9) CONVERT Source_Event_IDs TO ARRAY ---
if 'Source_Event_IDs' in standard_df.columns:
    standard_df['Source_Event_IDs'] = standard_df['Source_Event_IDs'].apply(
        lambda x: [str(x)] if pd.notna(x) else []
    )

# --- 10) LOCATION AS ARRAY OF STRINGS ---
if 'Location' in standard_df.columns and 'Country' in standard_df.columns:
    def listify_location(row):
        """
        If loc is already a list, return as-is; else make an empty list if None.
        If loc is NaN or an empty list, take the value from Country.
        """
        loc = row['Location']
        if isinstance(loc, list) and loc:
            # Make sure all elements are strings
            return [str(el) for el in loc]
        elif pd.notna(row['Country']):
            return [str(row['Country'])]
        return []
    
    standard_df['Location'] = standard_df.apply(listify_location, axis=1)

# --- 11) LATITUDE / LONGITUDE AS ARRAYS ---
if 'Latitude' in standard_df.columns:
    standard_df['Latitude'] = standard_df['Latitude'].apply(
        lambda val: [float(val)] if pd.notna(val) else []
    )

if 'Longitude' in standard_df.columns:
    standard_df['Longitude'] = standard_df['Longitude'].apply(
        lambda val: [float(val)] if pd.notna(val) else []
    )

# --- 12) SET EXTERNAL_LINKS, COMMENTS, SOURCE ---
if 'External_Links' in standard_df.columns:
    standard_df['External_Links'] = [[] for _ in range(len(standard_df))]

if 'Comments' in standard_df.columns:
    standard_df['Comments'] = standard_df['Comments'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

if 'Source' in standard_df.columns:
    # If you want to default everything to ["GDACS"]:
    # standard_df['Source'] = [["GDACS"]]*len(standard_df)
    # Or just convert any existing value to an array:
    standard_df['Source'] = standard_df['Source'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# --- 13) CONVERT DATE, THEN DERIVE YEAR/MONTH/DAY/TIME IF MISSING ---
if 'Date' in standard_df.columns:
    standard_df['Date'] = pd.to_datetime(standard_df['Date'], errors='coerce')
    # If 'Year' was not set or is NaN, fill it
    if 'Year' in standard_df.columns:
        missing_year = standard_df['Year'].isna()
        standard_df.loc[missing_year, 'Year'] = standard_df.loc[missing_year, 'Date'].dt.year
    else:
        standard_df['Year'] = standard_df['Date'].dt.year
    
    standard_df['Month'] = standard_df['Date'].dt.month
    standard_df['Day'] = standard_df['Date'].dt.day
    standard_df['Time'] = standard_df['Date'].dt.strftime('%H:%M:%S')
    # Just keep a YYYY-MM-DD
    standard_df['Date'] = standard_df['Date'].dt.strftime('%Y-%m-%d')

# --- 14) SEVERITY / ALERT_LEVEL AS ARRAYS ---
if 'Severity' in standard_df.columns:
    standard_df['Severity'] = standard_df['Severity'].apply(
        lambda x: [str(x)] if pd.notna(x) else []
    )

if 'Alert_Level' in standard_df.columns:
    standard_df['Alert_Level'] = standard_df['Alert_Level'].apply(
        lambda x: [x] if pd.notna(x) else []
    )

# --- 15) POPULATION AFFECTED TO INT ---
if 'Population_Affected' in standard_df.columns:
    standard_df['Population_Affected'] = standard_df['Population_Affected'].apply(
        lambda x: int(x) if pd.notna(x) else None
    )

# --- 16) CONVERT YEAR/MONTH/DAY TO INT ---
for col in ['Year', 'Month', 'Day']:
    if col in standard_df.columns:
        standard_df[col] = standard_df[col].apply(
            lambda x: int(x) if pd.notna(x) else None
        )

# --- 17) NULL OUT ANY EMPTY TIME ---
if 'Time' in standard_df.columns:
    standard_df['Time'] = standard_df['Time'].where(pd.notna(standard_df['Time']), None)

# --- 18) REPLACE NAN WITH None ---
standard_df = standard_df.astype(object).where(pd.notnull(standard_df), None)

# --- 19) VALIDATE AGAINST SCHEMA ---
for i, record in standard_df.iterrows():
    record_dict = record.to_dict()
    try:
        validate(instance=record_dict, schema=schema)
    except ValidationError as e:
        print(f"Record {i} failed validation: {e.message}")

# --- 20) OPTIONAL: DUMP ARRAY COLUMNS AS JSON STRINGS BEFORE CSV (IF DESIRED) ---
# array_fields = [
#     'Source_Event_IDs', 'Location', 'Latitude', 'Longitude',
#     'Source', 'Comments', 'External_Links', 'Severity', 'Alert_Level'
# ]
# for col in array_fields:
#     if col in standard_df.columns:
#         standard_df[col] = standard_df[col].apply(
#             lambda arr: json.dumps(arr) if arr is not None else '[]'
#         )

# --- 21) REPLACE ANY LEFTOVER NAN WITH '' FOR CSV OUTPUT ---
standard_df = standard_df.replace({np.nan: ''})

# --- 22) WRITE STANDARDIZED CSV ---
standard_df.to_csv(OUTPUT_CSV, index=False)
print(f"Standardization complete. Output written to {OUTPUT_CSV}")
