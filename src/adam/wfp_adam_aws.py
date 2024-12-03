import requests
import os
import pandas as pd
from datetime import datetime

BASE_URL = "https://exie6ocssxnczub3aslzanna540gfdjs.lambda-url.eu-west-1.on.aws/events/"

EVENT_TYPES = {
    "earthquakes": {
        "name": "{iso3}-earthquake-{event_id}",
        "title": "{iso3}: Earthquake - {mag}M",
        "description": "Magnitude {mag} earthquake at {depth} depth occurred on {published_at} in {place}.",
    },
    "cyclones": {
        "name": "{iso3}-cyclone-{event_id}",
        "title": "{iso3}: Cyclone - {storm_status}",
        "description": "Cyclone ({storm_status.lower()}) during the period {from_date}-{to_date} in {countries}.",
    },
    "floods": {
        "name": "{iso3}-flood-{event_id}",
        "title": "{iso3}: Flood",
        "description": "Flood covering {flood_area} sq m on {effective_date} in {country}.",
    },
}

OUTPUT_DIR = "./data/adam_events"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_event_data(event_type, start_date, end_date):
    url = f"{BASE_URL}{event_type}?start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code} for {event_type}")
        print(response.text)
        return []

    return response.json()

def process_events(event_type, events):
    processed_data = []
    for event in events:
        properties = event.get("properties", {})
        properties["event_type"] = event_type
        processed_data.append(properties)

    return pd.DataFrame(processed_data)

def save_to_csv(event_type, dataframe):
    if dataframe.empty:
        print(f"No data found for {event_type}")
        return

    output_file = os.path.join(OUTPUT_DIR, f"{event_type}_events.csv")
    dataframe.to_csv(output_file, index=False)
    print(f"Saved {event_type} data to {output_file}")

def main():
    start_date = "2000-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    for event_type in EVENT_TYPES.keys():
        print(f"Fetching data for {event_type}")
        events = fetch_event_data(event_type, start_date, end_date)
        if not events:
            print(f"No events found for {event_type}")
            continue

        dataframe = process_events(event_type, events)
        save_to_csv(event_type, dataframe)

if __name__ == "__main__":
    main()
