import os
import pandas as pd
import numpy as np
from dictionary import (
    STANDARD_COLUMNS, GLIDE_MAPPING, GDACS_MAPPING, ADAM_MAPPING,
    CERF_MAPPING, DISASTER_CHARTER_MAPPING
)

glide_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/glide/glide_data_combined_all.csv')
gdacs_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v2_fast/combined_gdacs_data.csv')
adam_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/adam_data/adam_eq_buffers.csv')
cerf_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/cerf/cerf_emergency_data_dynamic_web_scrape.csv')
disaster_charter_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/disaster-charter/charter_activations_web_scrape_2000_2024.csv')

def apply_mapping(df, mapping, standard_columns, source_name):
    df = df.copy()
    columns_to_rename = {}
    for standard_col, original_col in mapping.items():
        if original_col and original_col in df.columns:
            if standard_col in df.columns:
                df.rename(columns={standard_col: f"{standard_col}_original"}, inplace=True)
            columns_to_rename[original_col] = standard_col
    df.rename(columns=columns_to_rename, inplace=True)
    for col in standard_columns:
        if col not in df.columns:
            df[col] = np.nan
    df['Source'] = source_name
    return df

glide_events_df = apply_mapping(glide_events_df, GLIDE_MAPPING, STANDARD_COLUMNS, 'GLIDE')
gdacs_events_df = apply_mapping(gdacs_events_df, GDACS_MAPPING, STANDARD_COLUMNS, 'GDACS')
adam_events_df = apply_mapping(adam_events_df, ADAM_MAPPING, STANDARD_COLUMNS, 'WFP_ADAM')
cerf_events_df = apply_mapping(cerf_events_df, CERF_MAPPING, STANDARD_COLUMNS, 'CERF')
disaster_charter_events_df = apply_mapping(disaster_charter_events_df, DISASTER_CHARTER_MAPPING, STANDARD_COLUMNS, 'Disaster_Charter')

def parse_dates(df, date_format=None):
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format=date_format, errors='coerce')
    return df

glide_events_df = parse_dates(glide_events_df, date_format='%Y/%m/%d')
gdacs_events_df = parse_dates(gdacs_events_df)
cerf_events_df = parse_dates(cerf_events_df)
disaster_charter_events_df = parse_dates(disaster_charter_events_df, date_format='%d/%m/%Y')

import pycountry

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return np.nan

for df in [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]:
    df['Country_Code'] = df['Country'].apply(get_country_code)

standard_event_types = {
    'Earthquake': 'Earthquake',
    'Flood': 'Flood',
    'Cyclone': 'Cyclone',
    'Hurricane': 'Cyclone',
    'Typhoon': 'Cyclone',
    'Tsunami': 'Tsunami',
}

def standardize_event_type(event_type):
    if pd.isnull(event_type):
        return np.nan
    event_type_lower = event_type.lower()
    for key in standard_event_types:
        if key.lower() in event_type_lower:
            return standard_event_types[key]
    return event_type

for df in [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]:
    df['Event_Type'] = df['Event_Type'].astype(str).apply(standardize_event_type)

df_list = [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]
for df in df_list:
    df['Source'] = df['Source'].fillna('').astype(str)
    df['Event_ID'] = df['Event_ID'].fillna('').astype(str)
    df['Event_Name'] = df['Event_Name'].fillna('').astype(str)
    df['Source_Event_ID'] = df['Source'] + '_' + df['Event_ID']

all_events_df = pd.concat(df_list, ignore_index=True)

final_columns = STANDARD_COLUMNS + ['Source_Event_ID', 'Source']
all_events_df = all_events_df[final_columns]

os.makedirs('./data/unified', exist_ok=True)
all_events_df.to_csv('./data/unified/unified_disaster_events.csv', index=False)

print(all_events_df.head())
