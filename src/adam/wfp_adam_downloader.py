import requests
import pandas as pd
import os

# Base URL for the FeatureServer
BASE_URL = "https://services3.arcgis.com/t6lYS2Pmd8iVx1fy/ArcGIS/rest/services/ADAM_Earthquake_And_Tropical_Storm_Events/FeatureServer"
OUTPUT_DIR = "./data/adam_data"

# Create the output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_layer_data(layer_id):
    """
    Fetch all records from a specific layer in batches, including geometry (x, y) if available.
    """
    layer_url = f"{BASE_URL}/{layer_id}/query"
    params = {
        "f": "json",
        "where": "1=1",  # No filtering; fetch all data
        "outFields": "*",  # Fetch all fields
        "returnGeometry": "true",  # Include geometry
        "resultOffset": 0,  # Start at the first record
        "resultRecordCount": 2000,  # Max records per batch
    }

    all_data = []
    while True:
        response = requests.get(layer_url, params=params)
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code} for layer {layer_id}")
            print(response.text)
            break

        data = response.json()
        features = data.get("features", [])
        print(f"Fetched {len(features)} records from layer {layer_id} (offset: {params['resultOffset']})")

        if not features:
            break

        for feature in features:
            attributes = feature["attributes"]
            geometry = feature.get("geometry", {})
            attributes["x"] = geometry.get("x", None)
            attributes["y"] = geometry.get("y", None)
            all_data.append(attributes)

        # Update offset for the next batch
        params["resultOffset"] += len(features)

    return all_data


def save_layer_to_csv(layer_id, layer_name):
    """
    Save data from a specific layer to a CSV file.
    """
    print(f"Fetching data for layer {layer_id}: {layer_name}")
    data = fetch_layer_data(layer_id)
    if data:
        df = pd.DataFrame(data)
        output_file = os.path.join(OUTPUT_DIR, f"{layer_name}.csv")
        df.to_csv(output_file, index=False)
        print(f"Layer {layer_name} saved to {output_file}. Total records: {len(df)}")
    else:
        print(f"No data found for layer {layer_id}: {layer_name}")


def main():
    # Layer IDs and names (from ArcGIS REST Service Directory)
    layers = {
        1: "adam_eq_events",
        2: "adam_ts_events",
        3: "adam_fl_events",
        4: "adam_fl_alerts",
        5: "adam_ts_nodes",
        6: "adam_ts_tracks",
        7: "adam_eq_buffers",
        8: "adam_ts_buffers",
        9: "adam_eq_shakemap",
    }

    for layer_id, layer_name in layers.items():
        save_layer_to_csv(layer_id, layer_name)


if __name__ == "__main__":
    main()
