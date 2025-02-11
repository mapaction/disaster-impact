import os
import ast
import hashlib
import pandas as pd
import time
import re

DATA_PATH = './data_mid/data_standardised/'
OUTPUT_PATH = './data_out/data_unified/'
GROUP_KEY = ['Event_Type', 'Country']

def load_data(data_path: str) -> dict:
    filenames = [
        "glide_standardised.csv", 
        "gdacs_standardised.csv", 
        "disaster_charter_standardised.csv",
        "emdat_standardised.csv", 
        "idmc_standardised.csv", 
        "cerf_standardised.csv",
        "ifrc_standardised.csv"
    ]
    dataframes = {}
    for filename in filenames:
        key = filename.replace('_standardised.csv', '')
        df = pd.read_csv(os.path.join(data_path, filename))
        dataframes[key] = df
    return dataframes

def prefix_event_ids(value, prefix: str):
    if pd.isna(value):
        return None
    if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
        try:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, list):
                parsed = [parsed]
            return [f"{prefix}_{item}" for item in parsed]
        except:
            return f"{prefix}_{value}"
    else:
        if isinstance(value, list):
            return [f"{prefix}_{item}" for item in value]
        else:
            return f"{prefix}_{value}"

def apply_prefixes(dataframes: dict) -> dict:
    for name, df in dataframes.items():
        if "Event_ID" in df.columns:
            df["Event_ID"] = df["Event_ID"].apply(lambda x: prefix_event_ids(x, name))
    return dataframes

def consolidate_group(group: pd.DataFrame) -> dict:
    consolidated_row = {}
    event_ids = sorted(set(group['Event_ID'].dropna().astype(str).tolist()))
    consolidated_row["Event_ID"] = event_ids
    unique_str = "|".join(event_ids)
    disaster_impact_id = "DI_" + hashlib.md5(unique_str.encode("utf-8")).hexdigest()
    consolidated_row["Disaster_Impact_ID"] = disaster_impact_id
    for column in group.columns:
        if column in GROUP_KEY or column == "Event_ID" or column == "Disaster_Impact_ID":
            if column == "Disaster_Impact_ID":
                continue
            consolidated_row[column] = sorted(set(group[column].dropna().astype(str).tolist()))
        else:
            values = group[column].dropna().tolist()
            if values:
                if all(isinstance(val, list) for val in values):
                    flat_values = [item for sublist in values for item in sublist]
                    consolidated_row[column] = sorted(set(map(str, flat_values)))
                else:
                    consolidated_row[column] = sorted(set(map(str, values)))
            else:
                consolidated_row[column] = None
    return consolidated_row

def group_by_date_range(data: pd.DataFrame, date_col: str, days: int = 7) -> pd.DataFrame:
    rows = []
    used_indices = set()
    for idx, row in data.iterrows():
        if idx in used_indices:
            continue
        start_date, end_date = row['Date_Group']
        matching_rows = data[
            (data[date_col] >= start_date) &
            (data[date_col] <= end_date) &
            (data['Event_Type'] == row['Event_Type']) &
            (data['Country'] == row['Country'])
        ]
        used_indices.update(matching_rows.index)
        rows.append(consolidate_group(matching_rows))
    return pd.DataFrame(rows)

def unify_data(dataframes: dict) -> pd.DataFrame:
    all_data = pd.concat(dataframes.values(), ignore_index=True)
    all_data['Date'] = pd.to_datetime(all_data['Date'])
    all_data['Date_Group'] = all_data['Date'].apply(
        lambda x: (x - pd.Timedelta(days=7), x + pd.Timedelta(days=7))
    )
    unified_df = group_by_date_range(all_data, 'Date')
    cols = ['Disaster_Impact_ID', 'Event_ID'] + [
        c for c in unified_df.columns 
        if c not in ('Disaster_Impact_ID','Event_ID')
    ]
    unified_df = unified_df[cols]
    return unified_df

def main():
    standardised_dfs = load_data(DATA_PATH)
    standardised_dfs = apply_prefixes(standardised_dfs)
    unified_df = unify_data(standardised_dfs)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    time.sleep(5)
    output_file = os.path.join(OUTPUT_PATH, 'unified_data.csv')
    def remove_time(date_str):
        return re.sub(r'\s+\d{2}:\d{2}:\d{2}$', '', date_str)
    unified_df['Date'] = unified_df['Date'].apply(lambda lst: [remove_time(item) for item in lst])

    unified_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()
