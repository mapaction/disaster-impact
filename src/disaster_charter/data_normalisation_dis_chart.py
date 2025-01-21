import pandas as pd
import json
import os
import re

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    DISASTER_CHARTER_MAPPING,
)

DISASTER_CHARTER_INPUT_CSV = "./data/disaster-charter/disaster_activations_boosted_dec.csv"
SCHEMA_PATH_DISASTER_CHARTER = "./src/disaster_charter/disaster_charter_schema.json"

def extract_event_type_from_event_name(df: pd.DataFrame, event_name_col: str = 'Event_Name', event_type_col: str = 'Event_Type') -> pd.DataFrame:
    if event_name_col in df.columns and event_type_col in df.columns:
        def extract_event_type(row):
            if pd.isna(row[event_type_col]) or not row[event_type_col]:
                if isinstance(row[event_name_col], str):
                    match = re.search(r'^(.*?)\s+in\s+', row[event_name_col])
                    if match:
                        return match.group(1).strip()
            return row[event_type_col]

        df[event_type_col] = df.apply(extract_event_type, axis=1)
    return df

def remove_float_suffix(value):
    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            if isinstance(item, float) and item.is_integer():
                cleaned_list.append(str(int(item)))
            else:
                cleaned_list.append(str(item))
        return cleaned_list
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

with open(SCHEMA_PATH_DISASTER_CHARTER, "r") as schema_disaster_charter:
    disaster_schema = json.load(schema_disaster_charter)

disaster_charter_df_raw = pd.read_csv(DISASTER_CHARTER_INPUT_CSV)

#print(disaster_charter_df_raw.columns)

cleaned1_df = map_and_drop_columns(disaster_charter_df_raw, DISASTER_CHARTER_MAPPING)
# Extract Event_Type from Event_Name only if Event_Type is empty
cleaned1_df = extract_event_type_from_event_name(cleaned1_df, event_name_col='Event_Name', event_type_col='Event_Type')
cleaned2_df = change_data_type(cleaned1_df, disaster_schema)

# Remove the ".0" float suffix from Source_Event_IDs
if "Source_Event_IDs" in cleaned2_df.columns:
    cleaned2_df["Source_Event_IDs"] = cleaned2_df["Source_Event_IDs"].apply(remove_float_suffix)

os.makedirs("./data_mid/disaster_charter/cleaned_inspection", exist_ok=True)
cleaned2_df.to_csv("./data_mid/disaster_charter/cleaned_inspection/disaster_charter_cleaned.csv", index=False)
