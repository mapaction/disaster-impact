import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Monty API URL
base_url = "https://monty-api.ifrc.org/data/JSON"
api_token = os.getenv("MONTY_API_TOKEN")
if not api_token:
    raise ValueError("API token not found. Please set 'MONTY_API_TOKEN' in your environment variables.")

# Metadata fields (from Montandon Metadata Documentation)
metadata_fields = [
    "coded_name", "ID_linkage", "spatial", "temporal", "allhaz_class", "event_ID",
    "ev_name", "all_ext_IDs", "all_hazs_Ab", "all_hazs_spec", "ev_ISO3s",
    "gen_location", "ev_sdate", "ev_fdate", "source", "hazard_detail",
    "haz_sub_ID", "haz_ext_IDs", "haz_Ab", "haz_spec", "haz_maxvalue",
    "haz_maxunits", "haz_src_db", "haz_src_org", "haz_src_URL", "haz_sdate",
    "haz_fdate", "haz_credate", "haz_moddate", "imp_sub_ID", "exp_spec",
    "imp_value", "imp_units", "imp_src_db", "imp_src_org", "imp_src_URL",
    "imp_sdate", "imp_fdate", "imp_credate", "imp_moddate", "res_sub_ID",
    "haz_spat_ID", "haz_spat_fileloc", "haz_spat_srcdb", "haz_spat_srcorg",
    "haz_spat_URL", "haz_ISO3s", "haz_lon", "haz_lat", "haz_spat_covcode",
    "haz_spat_res", "haz_spat_resunits", "haz_spat_crs", "haz_spat_unit",
    "ISO3", "country", "unregion", "worldbankregion", "continent",
    "unsubregion", "worldbankincomegroup", "exp_spec_code", "exp_spec_lab",
    "exp_subcat_code", "exp_subcat_lab", "exp_cat_code", "exp_cat_lab",
    "haz_spec_code", "haz_spec_lab", "haz_cluster_code", "haz_cluster_lab",
    "spat_cov_code", "spat_cov_lab", "src_org_code", "src_org_lab",
    "src_org_email", "src_db_code", "src_db_lab", "src_db_attr",
    "src_db_lic", "src_db_URL", "src_addinfo", "unit_codes", "units_lab",
    "unit_groups_code", "unit_groups_lab"
]

# Fetch Monty API data
def fetch_monty_data():
    sdate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"{base_url}?Mtoken={api_token}&sdate={sdate}"
    print(f"Requesting data from URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully retrieved data for {sdate}.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Monty API: {e}")
        return None

# Flatten and combine Monty data into a single table
def combine_data(data):
    combined_rows = []

    def extract_values(item, parent_key=""):
        """Recursively extract values from nested dictionaries."""
        if isinstance(item, dict):
            for key, value in item.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                yield from extract_values(value, full_key)
        elif isinstance(item, list):
            for i, value in enumerate(item):
                yield from extract_values(value, f"{parent_key}[{i}]")
        else:
            yield parent_key, item

    # Iterate through each top-level section in the API response
    for section, records in data.items():
        if isinstance(records, list):  # Handle list sections (e.g., event_Level)
            for record in records:
                row = dict(extract_values(record))
                row["section"] = section  # Add section name for context
                combined_rows.append(row)
        elif isinstance(records, dict):  # Handle dict sections (e.g., monty_Info)
            row = dict(extract_values(records))
            row["section"] = section
            combined_rows.append(row)

    return pd.DataFrame(combined_rows)

# Main execution
if __name__ == "__main__":
    print("Fetching Monty API data...")
    monty_data = fetch_monty_data()
    if monty_data:
        print("Combining Monty API data into a single CSV...")
        df = combine_data(monty_data)

        # Ensure all metadata fields are included
        for field in metadata_fields:
            if field not in df.columns:
                df[field] = None  # Add missing fields as empty

        # Save to a single CSV
        output_file = "monty_combined_metadata.csv"
        df.to_csv(output_file, index=False)
        print(f"Combined data saved to {output_file}")
