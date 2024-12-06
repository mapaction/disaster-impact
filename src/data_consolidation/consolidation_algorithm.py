import os
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
import pycountry
from dictionary import (
    STANDARD_COLUMNS, GLIDE_MAPPING, GDACS_MAPPING, ADAM_MAPPING,
    CERF_MAPPING, DISASTER_CHARTER_MAPPING
)

if len(STANDARD_COLUMNS) != len(set(STANDARD_COLUMNS)):
    print("Warning: STANDARD_COLUMNS contains duplicates:")
    duplicates = pd.Series(STANDARD_COLUMNS).duplicated(keep=False)
    print(pd.Series(STANDARD_COLUMNS)[duplicates])

print("STANDARD_COLUMNS:", STANDARD_COLUMNS)

glide_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/glide/glide_data_combined_all.csv')
gdacs_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v2_fast/combined_gdacs_data.csv')
adam_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/adam_data/adam_eq_buffers.csv')
cerf_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/cerf/cerf_emergency_data_dynamic_web_scrape.csv')
disaster_charter_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/disaster-charter/charter_activations_web_scrape_2000_2024.csv')

def remove_duplicate_columns(df):
    duplicates = df.columns[df.columns.duplicated()]
    if duplicates.any():
        print(f"Duplicate columns removed: {list(duplicates)}")
    return df.loc[:, ~df.columns.duplicated()]

dataframes = [glide_events_df, gdacs_events_df, adam_events_df, cerf_events_df, disaster_charter_events_df]
dataframe_names = ['GLIDE', 'GDACS', 'WFP_ADAM', 'CERF', 'Disaster_Charter']

for i, df in enumerate(dataframes):
    print(f"--- Processing {dataframe_names[i]} ---")
    print("Columns before removing duplicates:", df.columns.tolist())
    df = remove_duplicate_columns(df)
    df.reset_index(drop=True, inplace=True)
    dataframes[i] = df

glide_events_df, gdacs_events_df, adam_events_df, cerf_events_df, disaster_charter_events_df = dataframes

def apply_mapping(df, mapping, standard_columns, source_name):
    df = df.copy()
    columns_to_rename = {v: k for k, v in mapping.items() if v}
    print(f"Applying mapping for {source_name}:")
    print("Columns before rename:", df.columns.tolist())
    df.rename(columns=columns_to_rename, inplace=True)
    print("Columns after rename:", df.columns.tolist())
    df = df.loc[:, ~df.columns.duplicated()]
    for col in standard_columns:
        if col not in df.columns:
            df[col] = np.nan
    df['Source'] = source_name
    final_cols = STANDARD_COLUMNS
    if 'Source' not in final_cols:
        final_cols.append('Source')
    df = df[final_cols]
    print("Columns after aligning to STANDARD_COLUMNS:", df.columns.tolist())
    return df

glide_events_df = apply_mapping(glide_events_df, GLIDE_MAPPING, STANDARD_COLUMNS, 'GLIDE')
gdacs_events_df = apply_mapping(gdacs_events_df, GDACS_MAPPING, STANDARD_COLUMNS, 'GDACS')
adam_events_df = apply_mapping(adam_events_df, ADAM_MAPPING, STANDARD_COLUMNS, 'WFP_ADAM')
cerf_events_df = apply_mapping(cerf_events_df, CERF_MAPPING, STANDARD_COLUMNS, 'CERF')
disaster_charter_events_df = apply_mapping(disaster_charter_events_df, DISASTER_CHARTER_MAPPING, STANDARD_COLUMNS, 'Disaster_Charter')

def parse_dates(df, column):
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%dT%H:%M:%S']
    for fmt in formats:
        temp = pd.to_datetime(df[column], format=fmt, errors='coerce')
        if temp.notnull().sum() > 0:
            df[column] = temp
            break
    return df

for df, name in zip([glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df],
                     ['GLIDE', 'GDACS', 'CERF', 'Disaster_Charter']):
    if 'Date' in df.columns:
        df = parse_dates(df, 'Date')

def get_country_code(name):
    if pd.isnull(name):
        return np.nan
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return np.nan

for df, name in zip([glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df],
                    ['GLIDE', 'GDACS', 'CERF', 'Disaster_Charter']):
    if 'Country_Code' in df.columns and df['Country_Code'].isnull().all():
        df['Country_Code'] = df['Country'].apply(get_country_code)
    elif 'Country_Code' not in df.columns:
        df['Country_Code'] = df['Country'].apply(get_country_code)

standard_event_types = {
    'Earthquake': 'Earthquake',
    'Flood': 'Flood',
    'Cyclone': 'Cyclone',
    'Hurricane': 'Cyclone',
    'Typhoon': 'Cyclone',
    'Tsunami': 'Tsunami'
}

def standardize_event_type(event_type):
    if pd.isnull(event_type):
        return np.nan
    event_type_lower = event_type.lower()
    for key, val in standard_event_types.items():
        if key.lower() in event_type_lower:
            return val
    return event_type

for df, name in zip([glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df],
                    ['GLIDE', 'GDACS', 'CERF', 'Disaster_Charter']):
    df['Event_Type'] = df['Event_Type'].astype(str).apply(standardize_event_type)

adam_events_df['Event_Type'] = adam_events_df['Event_Type'].astype(str).apply(standardize_event_type)
if 'Country_Code' not in adam_events_df.columns:
    adam_events_df['Country_Code'] = adam_events_df['Country'].apply(get_country_code)

def ensure_columns(df, standard_columns):
    needed_cols = standard_columns
    if 'Source' not in needed_cols:
        needed_cols.append('Source')
    for col in needed_cols:
        if col not in df.columns:
            df[col] = np.nan
    df = df.loc[:, ~df.columns.duplicated()]
    return df[needed_cols]

glide_events_df = ensure_columns(glide_events_df, STANDARD_COLUMNS)
gdacs_events_df = ensure_columns(gdacs_events_df, STANDARD_COLUMNS)
adam_events_df = ensure_columns(adam_events_df, STANDARD_COLUMNS)
cerf_events_df = ensure_columns(cerf_events_df, STANDARD_COLUMNS)
disaster_charter_events_df = ensure_columns(disaster_charter_events_df, STANDARD_COLUMNS)

df_list = [glide_events_df, gdacs_events_df, adam_events_df, cerf_events_df, disaster_charter_events_df]

for df, name in zip(df_list, dataframe_names):
    print(f"DataFrame {name} final columns:", df.columns.tolist())
    if not df.index.is_unique:
        print(f"Warning: {name} DataFrame index is not unique. Resetting...")
        df.index = range(len(df))

all_events_df = pd.concat(df_list, ignore_index=True)
print("Concatenation successful!")

def generate_composite_key(df):
    df['Composite_Key'] = df['Event_Type'].fillna('') + '_' + \
                          df['Country_Code'].fillna('') + '_' + \
                          df['Date'].astype(str).fillna('')
    return df

all_events_df = generate_composite_key(all_events_df)
print(f"Duplicate composite keys before dropping: {all_events_df['Composite_Key'].duplicated().sum()}")
all_events_df.drop_duplicates(subset=['Composite_Key'], inplace=True)

def fuzzy_match(name1, name2):
    if pd.isnull(name1) or pd.isnull(name2):
        return 0
    return fuzz.ratio(name1, name2)

def find_fuzzy_matches(df, threshold=80):
    df['Fuzzy_Match_Score'] = df['Event_Name'].apply(lambda x: fuzz.ratio(x, x) if pd.notnull(x) else 0)
    return df[df['Fuzzy_Match_Score'] >= threshold]

all_events_df = find_fuzzy_matches(all_events_df)

grouped = all_events_df.groupby('Composite_Key')

def consolidate_group(group):
    event_ids = group['Event_ID'].tolist()
    sources = group['Source'].tolist() if 'Source' in group.columns else [np.nan]*len(group)
    event_ids_str = [str(eid) for eid in event_ids if pd.notnull(eid)]
    sources_str = [str(src) for src in sources if pd.notnull(src)]
    consolidated = {
        'Cluster_ID': group.name,
        'Event_IDs': '; '.join(event_ids_str),
        'Sources': '; '.join(sources_str),
        'Event_Name': group['Event_Name'].dropna().iloc[0] if group['Event_Name'].notnull().any() else np.nan,
        'Event_Type': group['Event_Type'].dropna().iloc[0] if group['Event_Type'].notnull().any() else np.nan,
        'Country': group['Country'].dropna().iloc[0] if group['Country'].notnull().any() else np.nan,
        'Date': group['Date'].dropna().iloc[0] if group['Date'].notnull().any() else np.nan,
        'Latitude': group['Latitude'].dropna().iloc[0] if group['Latitude'].notnull().any() else np.nan,
        'Longitude': group['Longitude'].dropna().iloc[0] if group['Longitude'].notnull().any() else np.nan,
        'Severity': group['Severity'].dropna().iloc[0] if group['Severity'].notnull().any() else np.nan,
        'Population_Affected': group['Population_Affected'].dropna().iloc[0] if group['Population_Affected'].notnull().any() else np.nan,
    }
    return pd.Series(consolidated)

unified_df = grouped.apply(consolidate_group).reset_index(drop=True)

output_path = '/home/evangelos/src/disaster-impact/data/unified/unified_disaster_events.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
unified_df.to_csv(output_path, index=False)

print(f"Unified dataset saved to {output_path}")
print(unified_df.head())
