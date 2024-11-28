import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time


SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_paginated/"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_paginated_events(start_date, end_date, event_type, alert_levels):
    page_number = 1
    all_events = []
    while True:
        params = {
            "fromdate": start_date.strftime("%Y-%m-%d"),
            "todate": end_date.strftime("%Y-%m-%d"),
            "eventlist": event_type,
            "alertlevel": ";".join(alert_levels),
            "pagesize": 100,  # Max allowed
            "pagenumber": page_number,
        }
        print(f"Fetching {event_type} events from {params['fromdate']} to {params['todate']} - Page {page_number}...")
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
            # Wait 1 minute between page requests
            print("Waiting for 1 minute to avoid rate-limiting...")
            time.sleep(60)
        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            break
    return all_events

def main():
    start_date = datetime(2000, 1, 1)  # Starting date
    end_date = datetime(2024, 11, 28)  # Ending date
    interval = timedelta(days=30)  # Monthly intervals
    event_types = ["EQ", "TC", "FL", "VO", "DR", "WF"]  # Individual event types
    alert_levels = ["Green", "Orange", "Red"]  # All alert levels

    all_data = pd.DataFrame()
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + interval, end_date)
        for event_type in event_types:
            events = fetch_paginated_events(current_date, next_date, event_type, alert_levels)
            if events:
                df = pd.DataFrame(events)
                all_data = pd.concat([all_data, df], ignore_index=True)
            else:
                print(f"No events found for {event_type} from {current_date.date()} to {next_date.date()}.")
            # Wait 1 minute between event type requests
            print("Waiting for 1 minute before fetching the next event type...")
            time.sleep(60)
        current_date = next_date

    # Save to yearly CSVs
    if not all_data.empty:
        all_data["year"] = pd.to_datetime(all_data["from_date"], errors="coerce").dt.year
        for year, group in all_data.groupby("year"):
            output_file = os.path.join(OUTPUT_DIR, f"gdacs_events_{year}.csv")
            group.to_csv(output_file, index=False)
            print(f"Saved {len(group)} events to {output_file}")
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()
