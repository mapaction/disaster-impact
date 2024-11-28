import requests
import pandas as pd
import os
import time
from datetime import datetime

# Constants
SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_optimized/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch events with pagination for a single event type and date range
def fetch_paginated_events(event_type, alert_levels, start_date, end_date):
    page_number = 1
    all_events = []
    while True:
        params = {
            "fromdate": start_date,
            "todate": end_date,
            "eventlist": event_type,
            "alertlevel": ";".join(alert_levels),
            "pagesize": 100,  # Max allowed
            "pagenumber": page_number,
        }
        print(f"Fetching {event_type} events from {start_date} to {end_date} - Page {page_number}...")
        try:
            response = requests.get(SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            features = data.get("features", [])
            if not features:
                print(f"No more events found on page {page_number}.")
                break
            for feature in features:
                props = feature["properties"]
                all_events.append({
                    "event_id": props.get("eventid", "N/A"),
                    "event_type": props.get("eventtype", "N/A"),
                    "event_name": props.get("name", "N/A"),
                    "from_date": props.get("fromdate", "N/A"),
                    "to_date": props.get("todate", "N/A"),
                    "alert_level": props.get("alertlevel", "N/A"),
                    "countries": ", ".join(
                        f"{country['countryname']} ({country['iso3']})"
                        for country in props.get("affectedcountries", [])
                    ),
                    "population": props.get("population", "N/A"),
                    "severity": props.get("severitydata", {}).get("severity", "N/A"),
                    "alert_score": props.get("alertscore", "N/A"),
                    "datemodified": props.get("datemodified", "N/A"),
                })
            page_number += 1
            time.sleep(1)  # Short delay between pages
        except requests.RequestException as e:
            print(f"Error fetching page {page_number} for {event_type}: {e}")
            break
    return all_events

def main():
    # Define parameters
    event_types = ["EQ", "TC", "FL", "VO", "DR", "WF"]  # Individual event types
    alert_levels = ["Green", "Orange", "Red"]  # All alert levels
    date_ranges = [
        ("2000-01-01", "2009-12-31"),  # Adjust based on volume
        ("2010-01-01", "2019-12-31"),
        ("2020-01-01", "2024-11-28"),
    ]

    all_data = pd.DataFrame()

    for event_type in event_types:
        for start_date, end_date in date_ranges:
            events = fetch_paginated_events(event_type, alert_levels, start_date, end_date)
            if events:
                df = pd.DataFrame(events)
                all_data = pd.concat([all_data, df], ignore_index=True)
            else:
                print(f"No events found for {event_type} from {start_date} to {end_date}.")
            # Delay after processing a broader date range
            print("Waiting 1 minute before continuing...")
            time.sleep(60)

    # Save to CSV
    output_file = os.path.join(OUTPUT_DIR, "gdacs_all_events_2000_to_2024.csv")
    if not all_data.empty:
        all_data.to_csv(output_file, index=False)
        print(f"Saved {len(all_data)} events to {output_file}")
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()
