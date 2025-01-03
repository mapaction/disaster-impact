import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_all_types_yearly_v2_fast/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_events(start_date, end_date, event_type):
    params = {
        "fromDate": start_date.strftime("%Y-%m-%d"),
        "toDate": end_date.strftime("%Y-%m-%d"),
        "alertlevel": "Green;Orange;Red",
        "eventlist": event_type,
        "country": ""
    }
    print(f"Fetching {event_type} events from {params['fromDate']} to {params['toDate']}...")
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {
                "event_id": feature["properties"].get("eventid", "N/A"),
                "event_type": feature["properties"].get("eventtype", "N/A"),
                "event_name": feature["properties"].get("name", "N/A"),
                "from_date": feature["properties"].get("fromdate", "N/A"),
                "to_date": feature["properties"].get("todate", "N/A"),
                "alert_level": feature["properties"].get("alertlevel", "N/A"),
                "countries": ", ".join(
                    f"{c['countryname']} ({c['iso3']})"
                    for c in feature["properties"].get("affectedcountries", [])
                ),
                "population": feature["properties"].get("population", "N/A"),
                "severity": feature["properties"].get("severitydata", {}).get("severity", "N/A"),
                "alert_score": feature["properties"].get("alertscore", "N/A"),
                "bbox": feature.get("bbox", []),  # Extracting bbox
                "coordinates": feature.get("geometry", {}).get("coordinates", []),  # Extracting coordinates
            }
            for feature in data.get("features", [])
        ]
    except requests.RequestException as e:
        print(f"Request failed for {event_type} events {params['fromDate']} to {params['toDate']}: {e}")
        return []
    except ValueError as e:
        print(f"Invalid JSON response for {event_type} events {params['fromDate']} to {params['toDate']}: {e}")
        return []

def main():
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2024, 11, 28)
    interval = timedelta(days=30)
    event_types = ["EQ", "TS", "TC", "FL", "VO", "DR", "WF"]

    all_data = pd.DataFrame()
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + interval, end_date)
        for event_type in event_types:
            try:
                events = fetch_events(current_date, next_date, event_type)
                if events:
                    df = pd.DataFrame(events)
                    all_data = pd.concat([all_data, df], ignore_index=True)
                else:
                    print(f"No events found for {event_type} from {current_date.date()} to {next_date.date()}")
            except Exception as e:
                print(f"Unexpected error for {event_type} events {current_date.date()} to {next_date.date()}: {e}")
        current_date = next_date

    if not all_data.empty:
        all_data["year"] = pd.to_datetime(all_data["from_date"], errors="coerce").dt.year
        for year, group in all_data.groupby("year"):
            output_file = os.path.join(OUTPUT_DIR, f"gdacs_events_{year}.csv")
            group.to_csv(output_file, index=False)
            print(f"Saved {len(group)} events to {output_file}")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
