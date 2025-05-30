"""Utility functions for the project."""

import pandas as pd


def map_and_drop_columns(raw_data: pd.DataFrame, dictionary: dict) -> pd.DataFrame:
    """Renames columns in the raw_data DataFrame based.

    Args:
        raw_data (pd.DataFrame): The input DataFrame with raw data.
        dictionary (dict): A dictionary where keys are
        the new column names and values are the old column names.

    Returns:
        pd.DataFrame: A DataFrame with columns renamed and unnecessary columns dropped.
    """
    rename_mapping = {value: key for key, value in dictionary.items() if value}
    return raw_data[list(rename_mapping.keys())].rename(columns=rename_mapping)


def change_data_type(cleaned1_data: pd.DataFrame, json_schema: dict) -> pd.DataFrame:
    """Change the data types of columns in a DataFrame based on a JSON schema.

    Args:
        cleaned1_data (pd.DataFrame): The DataFrame with data to be type-casted.
        json_schema (dict): The JSON schema defining
        the desired data types for each column.

    Returns:
        pd.DataFrame: The DataFrame with columns cast to the specified data types.
    """
    for column, properties in json_schema["properties"].items():
        if column in cleaned1_data.columns:
            column_type = properties.get("type")
            if "array" in column_type:
                cleaned1_data[column] = cleaned1_data[column].apply(
                    lambda x: ",".join(map(str, x))
                    if isinstance(x, list)
                    else (str(x) if pd.notna(x) else ""),
                )
            elif "string" in column_type:
                cleaned1_data[column] = cleaned1_data[column].astype(str)
            elif "number" in column_type:
                cleaned1_data[column] = pd.to_numeric(
                    cleaned1_data[column],
                    errors="coerce",
                )
            elif "integer" in column_type:
                cleaned1_data[column] = pd.to_numeric(
                    cleaned1_data[column],
                    errors="coerce",
                ).astype("Int64")
            elif "null" in column_type:
                cleaned1_data[column] = cleaned1_data[column].where(
                    cleaned1_data[column].notna(),
                    None,
                )
    return cleaned1_data


def normalize_event_type(df: pd.DataFrame, event_code_csv: str) -> pd.DataFrame:
    """Normalizes the Event_Type.

    The CSV file is expected to have two columns with headers:
        - event_code: the normalized event type key.
        - event_name: the event type description.

    For each row in `df`, if the standardized Event_Type value matches a
    description from the CSV, the corresponding normalized key is stored in a
    new column, Event_Code. If no match is found, the original Event_Type value
    is retained.

    Args:
        df (pd.DataFrame): The input DataFrame containing an 'Event_Type' column.
        event_code_csv (str): The path to the CSV file containing the event code
            mapping.

    Returns:
        pd.DataFrame: The DataFrame with an additional 'Event_Code' column.
    """
    event_mapping_df = pd.read_csv(event_code_csv)
    event_mapping_df["event_name"] = (
        event_mapping_df["event_name"].str.strip().str.upper()
    )
    event_mapping_df["event_code"] = event_mapping_df["event_code"].str.strip()
    mapping = dict(
        zip(
            event_mapping_df["event_name"],
            event_mapping_df["event_code"],
            strict=False,
        ),
    )
    df["Event_Code"] = (
        df["Event_Type"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(mapping)
        .fillna(df["Event_Type"])
    )
    return df
