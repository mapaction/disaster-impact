import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

base_url = "https://monty-api.ifrc.org/data/JSON"
api_token = os.getenv("MONTY_API_TOKEN")
if not api_token:
    raise ValueError("API token not found. Please set 'MONTY_API_TOKEN' in your environment variables.")

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

def save_sections_to_csv(data):
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        for key, value in data.items():
            if isinstance(value, list):
                df = pd.DataFrame(value)
                output_file = os.path.join(output_dir, f"{key}.csv")
                df.to_csv(output_file, index=False)
                print(f"Saved {key} to {output_file}")
            elif isinstance(value, dict):
                output_file = os.path.join(output_dir, f"{key}.json")
                with open(output_file, "w") as f:
                    json.dump(value, f, indent=2)
                print(f"Saved {key} to {output_file} (JSON format)")
            else:
                print(f"Skipping {key} - unsupported data type: {type(value)}")
    except Exception as e:
        print(f"Error saving sections to CSV: {e}")

if __name__ == "__main__":
    print("Fetching Monty API data...")
    monty_data = fetch_monty_data()
    if monty_data:
        print("Saving Monty API data to CSV files...")
        save_sections_to_csv(monty_data)
        print("All sections processed and saved.")
