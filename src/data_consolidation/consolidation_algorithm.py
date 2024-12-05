import os
import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from geopy.distance import geodesic
from dictionary import (
    STANDARD_COLUMNS, GLIDE_MAPPING, GDACS_MAPPING, ADAM_MAPPING,
    CERF_MAPPING, DISASTER_CHARTER_MAPPING
)
glide_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/glide/glide_data_combined_all.csv')
gdacs_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v2_fast/combined_gdacs_data.csv')
adam_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/adam_data/adam_eq_buffers.csv')
cerf_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/cerf/cerf_emergency_data_dynamic_web_scrape.csv')
disaster_charter_events_df = pd.read_csv('/home/evangelos/src/disaster-impact/data/disaster-charter/charter_activations_web_scrape_2000_2024.csv')
print("GLIDE columns:", glide_events_df.columns)
print("GDACS columns:", gdacs_events_df.columns)
print("ADAM columns:", adam_events_df.columns)
print("CERF columns:", cerf_events_df.columns)
print("Disaster Charter columns:", disaster_charter_events_df.columns)

def apply_mapping(df, mapping, standard_columns, source_name):
    rename_dict = {original_col: standard_col for standard_col, original_col in mapping.items() if original_col}
    df = df.rename(columns=rename_dict)
    for col in standard_columns:
        if col not in df.columns:
            df[col] = np.nan
    df['Source'] = df['Source'].fillna(source_name) if 'Source' in df.columns else source_name
    return df

glide_events_df = apply_mapping(glide_events_df, GLIDE_MAPPING, STANDARD_COLUMNS, 'GLIDE')
gdacs_events_df = apply_mapping(gdacs_events_df, GDACS_MAPPING, STANDARD_COLUMNS, 'GDACS')
adam_events_df = apply_mapping(adam_events_df, ADAM_MAPPING, STANDARD_COLUMNS, 'WFP_ADAM')
cerf_events_df = apply_mapping(cerf_events_df, CERF_MAPPING, STANDARD_COLUMNS, 'CERF')
disaster_charter_events_df = apply_mapping(disaster_charter_events_df, DISASTER_CHARTER_MAPPING, STANDARD_COLUMNS, 'Disaster_Charter')

for df in [glide_events_df, gdacs_events_df, adam_events_df, cerf_events_df, disaster_charter_events_df]:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

import pycountry

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return np.nan

for df in [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]:
    if 'Country_Code' not in df.columns or df['Country_Code'].isnull().all():
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
    for key in standard_event_types:
        if key.lower() in event_type.lower():
            return standard_event_types[key]
    return event_type

for df in [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]:
    df['Event_Type'] = df['Event_Type'].astype(str).apply(standardize_event_type)

df_list = [glide_events_df, gdacs_events_df, cerf_events_df, disaster_charter_events_df]
for df in df_list:
    df['Event_Name'] = df['Event_Name'].astype(str)
    df['Event_ID'] = df['Event_ID'].astype(str)
    df['Source_Event_ID'] = df['Source'] + '_' + df['Event_ID']

all_events_df = pd.concat(df_list, ignore_index=True)
all_events_df.reset_index(inplace=True)
all_events_df.rename(columns={'index': 'Global_Event_Index'}, inplace=True)

def generate_composite_key(df):
    df['Composite_Key'] = df['Event_Type'].fillna('') + '_' + \
                          df['Country_Code'].fillna('') + '_' + \
                          df['Date'].dt.strftime('%Y-%m').fillna('')
    return df

all_events_df = generate_composite_key(all_events_df)
grouped = all_events_df.groupby('Composite_Key')
all_events_df['Cluster_ID'] = -1
current_cluster_id = 0
from tqdm.notebook import tqdm
tqdm.pandas()

def cluster_events(group):
    global current_cluster_id
    event_indices = group['Global_Event_Index'].tolist()
    event_names = group['Event_Name'].tolist()
    cluster_assignments = [-1] * len(event_indices)
    for i in range(len(event_indices)):
        if cluster_assignments[i] == -1:
            cluster_assignments[i] = current_cluster_id
            name_i = event_names[i]
            for j in range(i+1, len(event_indices)):
                if cluster_assignments[j] == -1:
                    name_j = event_names[j]
                    score = fuzz.token_set_ratio(name_i, name_j)
                    if score >= 80:
                        cluster_assignments[j] = current_cluster_id
            current_cluster_id += 1
    group = group.copy()
    group['Cluster_ID'] = cluster_assignments
    return group

all_events_df = grouped.apply(cluster_events).reset_index(drop=True)

def consolidate_cluster(cluster):
    consolidated = {}
    for col in STANDARD_COLUMNS + ['Source_Event_ID', 'Source']:
        values = cluster[col].dropna().unique()
        if len(values) == 1:
            consolidated[col] = values[0]
        else:
            consolidated[col] = '; '.join(map(str, values))
    return pd.Series(consolidated)

final_df = all_events_df.groupby('Cluster_ID').apply(consolidate_cluster).reset_index(drop=True)
unclustered_events = all_events_df[all_events_df['Cluster_ID'] == -1]
if not unclustered_events.empty:
    unclustered_consolidated = unclustered_events.apply(consolidate_cluster, axis=1)
    final_df = pd.concat([final_df, unclustered_consolidated], ignore_index=True)

adam_events_df['Latitude'] = pd.to_numeric(adam_events_df['Latitude'], errors='coerce')
adam_events_df['Longitude'] = pd.to_numeric(adam_events_df['Longitude'], errors='coerce')

def spatial_match_adam(row, adam_df, max_distance_km=100):
    lat1 = row['Latitude']
    lon1 = row['Longitude']
    if pd.isnull(lat1) or pd.isnull(lon1):
        return np.nan
    adam_df_valid = adam_df.dropna(subset=['Latitude', 'Longitude'])
    adam_df_valid['Distance'] = adam_df_valid.apply(
        lambda x: geodesic((lat1, lon1), (x['Latitude'], x['Longitude'])).kilometers, axis=1)
    close_events = adam_df_valid[adam_df_valid['Distance'] <= max_distance_km]
    if not close_events.empty:
        closest_event = close_events.loc[close_events['Distance'].idxmin()]
        return closest_event['Event_ID']
    else:
        return np.nan

final_df['Matched_ADAM_Event_ID'] = final_df.apply(lambda row: spatial_match_adam(row, adam_events_df), axis=1)
matched_adam_df = final_df[final_df['Matched_ADAM_Event_ID'].notnull()]
if not matched_adam_df.empty:
    matched_adam_df = matched_adam_df.merge(
        adam_events_df, left_on='Matched_ADAM_Event_ID', right_on='Event_ID', suffixes=('', '_ADAM'))
    for col in ['Latitude', 'Longitude', 'Date', 'Severity', 'Population_Affected']:
        col_ADAM = col + '_ADAM'
        if col_ADAM in matched_adam_df.columns:
            matched_adam_df[col] = matched_adam_df[col].combine_first(matched_adam_df[col_ADAM])
            matched_adam_df.drop(columns=[col_ADAM], inplace=True)
    final_df.update(matched_adam_df)

final_columns = STANDARD_COLUMNS + ['Source_Event_ID']
final_df = final_df[final_columns]
os.makedirs('./data/unified', exist_ok=True)
final_df.to_csv('./data/unified/unified_disaster_events.csv', index=False)
print(final_df.head())
