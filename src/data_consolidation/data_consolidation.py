import pandas as pd
import json
import os
import hashlib

from src.data_consolidation.dictionary import STANDARD_COLUMNS

os.makedirs('./data_mid/data_standardised', exist_ok=True)

UNIFIED_SCHEMA_PATH = "./src/unified/unified_json_schema/unified_schema.json"

GROUP_KEY = ['Event_Type', 'Country', 'Date']

dataframes = {
    "glide": pd.read_csv('./data_mid_2/glide/glide_mid2.csv').copy(),
    "gdacs": pd.read_csv('./data_mid_2/gdacs/gdacs_mid2.csv').copy(),
    "disaster_charter": pd.read_csv('./data_mid_2/disaster_charter/disaster_charter_mid2.csv').copy(),
    "emdat": pd.read_csv('./data_mid_2/emdat/emdat_mid2.csv').copy(),
    "idmc": pd.read_csv('./data_mid_2/idmc_idu/idus_mid2.csv').copy(),
    "cerf": pd.read_csv('./data_mid_2/cerf/cerf_mid2.csv').copy(),
    "ifrc": pd.read_csv('./data_mid_2/ifrc_eme/ifrc_eme_mid2.csv').copy()
}

with open(UNIFIED_SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

schema_properties = schema["properties"]

def get_default_value(data_type):
    """
    Returns the default value for a given data type.

    Parameters:
    data_type (str): The type of data ("string", "array", "integer", "number").

    Returns:
    None or list: Default value for the given data type. None for "string", "integer", and "number". Empty list for "array".
    """
    if data_type == "string":
        return None
    elif data_type == "array":
        return []
    elif data_type == "integer":
        return None
    elif data_type == "number":
        return None
    else:
        return None

def ensure_columns(df, standard_columns, schema_properties):
    """
    Ensure that the DataFrame contains all the standard columns.

    Parameters:
    df (pd.DataFrame): The input DataFrame to be checked and modified.
    standard_columns (list): A list of column names that should be present in the DataFrame.
    schema_properties (dict): A dictionary containing schema properties, where keys are column names and values are dictionaries with column properties.

    Returns:
    pd.DataFrame: A new DataFrame with all the standard columns, adding any missing columns with default values.
    """
    df = df.copy()
    for column in standard_columns:
        if column not in df.columns:
            data_type = schema_properties.get(column, {}).get("type", ["string"])[0]
            default_value = get_default_value(data_type)
            df.loc[:, column] = [default_value] * len(df)
    return df

def remove_duplicates(df):
    return df.drop_duplicates()

def consolidate_rows(df, group_key, schema_properties):
    """
    Consolidates rows in a DataFrame based on a group key and schema properties.

    Args:
        df (pd.DataFrame): The input DataFrame to be consolidated.
        group_key (list): List of column names to group by.
        schema_properties (dict): Dictionary defining the schema properties for each column.

    Returns:
        pd.DataFrame: A new DataFrame with consolidated rows.

    The function groups the DataFrame by the specified group key, consolidates the data within each group
    according to the schema properties, and generates a unique Event_ID for each group.
    """
    consolidated_data = []

    def consolidate_group(group):
        """
        Consolidates a group of data based on predefined schema properties.

        Args:
            group (pd.DataFrame): The group of data to be consolidated.

        Returns:
            dict: A dictionary containing the consolidated data.

        The function processes each column in the group according to its type defined in schema_properties.
        It handles arrays, dates, and other types, and generates a unique Event_ID based on Source_Event_IDs.
        """
        consolidated = {}
        for column in schema_properties.keys():
            if column in group.columns and column not in group_key:
                if schema_properties[column].get("type", ["string"])[0] == "array":
                    consolidated[column] = sorted(
                        set(
                            item for sublist in group[column].dropna()
                            for item in (sublist if isinstance(sublist, list) else [sublist])
                        )
                    )
                elif column == "Date":
                    date_str = group[column].dropna().iloc[0]
                    date_parsed = pd.to_datetime(date_str, errors='coerce')
                    consolidated[column] = (
                        date_parsed.strftime("%Y-%m-%d") if pd.notnull(date_parsed) else date_str
                    )
                else:
                    non_nan_values = group[column].dropna()
                    if len(non_nan_values) > 1:
                        consolidated[column] = non_nan_values.tolist()
                    else:
                        consolidated[column] = non_nan_values.iloc[0] if not non_nan_values.empty else None

        for key in group_key:
            consolidated[key] = group[key].iloc[0]

        source_ids = sorted(
            set(
                item
                for sublist in group["Source_Event_IDs"].dropna()
                for item in (sublist if isinstance(sublist, list) else [sublist])
            )
        )
        unique_str = "|".join(source_ids)
        event_id = hashlib.md5(unique_str.encode("utf-8")).hexdigest()
        consolidated["Event_ID"] = event_id
        return consolidated

    grouped = df.groupby(group_key)
    for _, group in grouped:
        consolidated_data.append(consolidate_group(group))

    consolidated_df = pd.DataFrame(consolidated_data)
    consolidated_df = ensure_columns(consolidated_df, STANDARD_COLUMNS, schema_properties)
    consolidated_df = consolidated_df[STANDARD_COLUMNS]
    return consolidated_df

def main():
    standardised_dataframes = {}
    for name, df in dataframes.items():
        df = remove_duplicates(df)
        df = ensure_columns(df, STANDARD_COLUMNS, schema_properties)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.strftime("%Y-%m-%d")
        consolidated_df = consolidate_rows(df, GROUP_KEY, schema_properties)
        standardised_dataframes[name] = consolidated_df

    for name, df in standardised_dataframes.items():
        output_path = f'./data_mid_3/data_standardised/{name}_standardised.csv'
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
