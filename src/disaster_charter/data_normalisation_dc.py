import pandas as pd
import json
import os
import re

from src.glide.data_normalisation_glide import (
    map_and_drop_columns,
    change_data_type,
)

from src.utils.azure_blob_utils import read_blob_to_dataframe

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    DISASTER_CHARTER_MAPPING,
)

SCHEMA_PATH_DISASTER_CHARTER = "./src/disaster_charter/disaster_charter_schema.json"
BLOB_NAME = "disaster-impact/raw/disaster-charter/charter_activations_web_scrape_2000_2024.csv"

def extract_event_type_from_event_name(df: pd.DataFrame, event_name_col: str = 'Event_Name', event_type_col: str = 'Event_Type') -> pd.DataFrame:
    """
    Extracts the event type from the event name if the event type is missing or empty.

    Args:
        df (pd.DataFrame): The DataFrame containing event data.
        event_name_col (str): The column name for event names. Default is 'Event_Name'.
        event_type_col (str): The column name for event types. Default is 'Event_Type'.

    Returns:
        pd.DataFrame: The DataFrame with the event type column updated.
    """
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
    """
    Convert float values to strings without decimal points if they are whole numbers.
    
    Args:
        value (float, list): A float or a list of floats to be processed.
        
    Returns:
        str, list: A string or a list of strings with whole number floats converted to integers.
    """
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

if __name__ == "__main__":
    with open(SCHEMA_PATH_DISASTER_CHARTER, "r") as schema_disaster_charter:
        disaster_schema = json.load(schema_disaster_charter)

    try:
        disaster_charter_df_raw = read_blob_to_dataframe(BLOB_NAME)
    except Exception as e:
        print(f"Failed to load CSV data from blob: {e}")
        exit(1)

    cleaned1_df = map_and_drop_columns(disaster_charter_df_raw, DISASTER_CHARTER_MAPPING)
    cleaned1_df = extract_event_type_from_event_name(cleaned1_df, event_name_col='Event_Name', event_type_col='Event_Type')
    cleaned2_df = change_data_type(cleaned1_df, disaster_schema)

    if "Source_Event_IDs" in cleaned2_df.columns:
        cleaned2_df["Source_Event_IDs"] = cleaned2_df["Source_Event_IDs"].apply(remove_float_suffix)

    os.makedirs("./data_mid/disaster_charter/cleaned_inspection", exist_ok=True)
    output_file_path = "./data_mid/disaster_charter/cleaned_inspection/disaster_charter_cleaned.csv"
    cleaned2_df.to_csv(output_file_path, index=False)

    print(f"Cleaned Disaster Charter data saved for inspection at: {output_file_path}")
