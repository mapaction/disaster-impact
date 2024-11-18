import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

base_url = "https://monty-api.ifrc.org/data/JSON"
api_token = os.getenv("MONTY_API_TOKEN")
if not api_token:
    raise ValueError("API token not found. Please set 'MONTY_API_TOKEN' in your environment variables.")

def fetch_event_level_data():
    url = f"{base_url}?Mtoken={api_token}"
    print(f"Requesting data from URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        event_level_data = data.get("event_Level", [])
        if not event_level_data:
            print("No event_Level data found.")
        else:
            print(f"Successfully retrieved {len(event_level_data)} records from event_Level.")
        return event_level_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Monty API: {e}")
        return None

def flatten_event_level(event_level_data):
    flattened_data = []
    for record in event_level_data:
        flat_record = {}
        
        if "ID_linkage" in record:
            flat_record["event_ID"] = record["ID_linkage"].get("event_ID", None)
            flat_record["ev_name"] = record["ID_linkage"].get("ev_name", None)

        if "all_ext_IDs" in record and isinstance(record["all_ext_IDs"], list):
            all_ext_IDs = record["all_ext_IDs"]
            flat_record["ext_IDs"] = "; ".join(ext.get("ext_ID", "NULL") for ext in all_ext_IDs)
            flat_record["ext_ID_db"] = "; ".join(ext.get("ext_ID_db", "NULL") for ext in all_ext_IDs)
            flat_record["ext_ID_org"] = "; ".join(ext.get("ext_ID_org", "NULL") for ext in all_ext_IDs)
        else:
            flat_record["ext_IDs"] = "NULL"
            flat_record["ext_ID_db"] = "NULL"
            flat_record["ext_ID_org"] = "NULL"

        if "temporal" in record:
            flat_record["ev_sdate"] = record["temporal"].get("ev_sdate", None)
            flat_record["ev_fdate"] = record["temporal"].get("ev_fdate", None)
        else:
            flat_record["ev_sdate"] = None
            flat_record["ev_fdate"] = None

        if "spatial" in record:
            flat_record["gen_location"] = record["spatial"].get("gen_location", None)
            flat_record["ev_ISO3s"] = record["spatial"].get("ev_ISO3s", None)
        else:
            flat_record["gen_location"] = None
            flat_record["ev_ISO3s"] = None

        if "allhaz_class" in record:
            allhaz_class = record["allhaz_class"]
            if isinstance(allhaz_class, list):
                flat_record["all_hazs_Ab"] = "; ".join(
                    haz.get("all_hazs_Ab", "NULL") if isinstance(haz, dict) else "NULL"
                    for haz in allhaz_class
                )
                flat_record["all_hazs_spec"] = "; ".join(
                    haz.get("all_hazs_spec", "NULL") if isinstance(haz, dict) else "NULL"
                    for haz in allhaz_class
                )
            elif isinstance(allhaz_class, str):
                flat_record["all_hazs_Ab"] = allhaz_class
                flat_record["all_hazs_spec"] = "NULL"
            else:
                flat_record["all_hazs_Ab"] = "NULL"
                flat_record["all_hazs_spec"] = "NULL"
        else:
            flat_record["all_hazs_Ab"] = "NULL"
            flat_record["all_hazs_spec"] = "NULL"

        flattened_data.append(flat_record)
    
    return pd.DataFrame(flattened_data)

def save_to_csv(df, filename="event_Level_cleaned.csv"):
    output_dir = "event_lvl_data"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    print("Fetching event_Level data...")
    event_level_data = fetch_event_level_data()
    if event_level_data:
        print("Flattening event_Level data...")
        event_level_df = flatten_event_level(event_level_data)
        print("Saving flattened data to CSV...")
        save_to_csv(event_level_df)
