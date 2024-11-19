import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

base_url = "https://monty-api.ifrc.org/data/JSON"
api_token = os.getenv("MONTY_API_TOKEN")
if not api_token:
    raise ValueError("API token not found. Please set 'MONTY_API_TOKEN' in your environment variables.")

def fetch_monty_data():
    """Fetch data from Monty API."""
    url = f"{base_url}?Mtoken={api_token}"
    print(f"Requesting data from URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Successfully retrieved data from Monty API.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Monty API: {e}")
        return None

def flatten_to_last_keys(data):
    """Flatten nested JSON, keeping only the last key as column title."""
    flattened = {}

    def recursive_flatten(obj, parent_key=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                recursive_flatten(value, key)  # Pass only the current key
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                recursive_flatten(item, parent_key)  # Keep the parent key for lists
        else:
            # Base case: store the value with the current key
            flattened[parent_key] = obj

    recursive_flatten(data)
    return flattened

def process_section(section_name, section_data):
    """Process a specific section of Monty data."""
    print(f"Processing section: {section_name}...")
    if isinstance(section_data, list):
        processed_data = []
        for record in section_data:
            processed_record = flatten_to_last_keys(record)
            processed_data.append(processed_record)
        return pd.DataFrame(processed_data)
    elif isinstance(section_data, dict):
        # For sections like monty_Info or taxonomies
        flattened_data = flatten_to_last_keys(section_data)
        return pd.DataFrame([flattened_data])  # Wrap in a list to create a DataFrame
    else:
        print(f"Skipping section: {section_name} (unsupported type)")
        return None

def save_to_csv(df, section_name):
    """Save DataFrame to a CSV file."""
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{section_name}_cleaned.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Data for {section_name} saved to {filepath}")

if __name__ == "__main__":
    print("Fetching Monty API data...")
    monty_data = fetch_monty_data()
    
    if monty_data:
        for section_name, section_data in monty_data.items():
            print(f"Processing section: {section_name}")
            processed_df = process_section(section_name, section_data)
            if processed_df is not None:
                save_to_csv(processed_df, section_name)
