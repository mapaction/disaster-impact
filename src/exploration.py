import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Monty API URL
base_url = "https://monty-api.ifrc.org/data/JSON"
api_token = os.getenv("MONTY_API_TOKEN")
if not api_token:
    raise ValueError("API token not found. Please set 'MONTY_API_TOKEN' in your environment variables.")

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

# Process each section of the data
def process_section(section_name, records):
    if not records:
        print(f"No data found for section: {section_name}")
        return None

    if isinstance(records, list):
        # Normalize list of records into a DataFrame
        df = pd.json_normalize(records)
        output_file = f"{section_name}.csv"
        df.to_csv(output_file, index=False)
        print(f"Saved {section_name} data to {output_file}")
        return df
    elif isinstance(records, dict):
        # Handle dictionary sections by converting to a single-row DataFrame
        df = pd.json_normalize(records)
        output_file = f"{section_name}_metadata.csv"
        df.to_csv(output_file, index=False)
        print(f"Saved {section_name} metadata to {output_file}")
        return df
    else:
        print(f"Unsupported data type for section: {section_name}")
        return None

# Main execution
if __name__ == "__main__":
    print("Fetching Monty API data...")
    monty_data = fetch_monty_data()
    if monty_data:
        print("Processing sections into structured CSVs...")
        for section_name, records in monty_data.items():
            process_section(section_name, records)
        print("All sections processed and saved to CSV files.")
