import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Constants
SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_all_types_yearly/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch events for a specific date range
def fetch_events(start_date, end_date, event_types):
    params = {
        "fromDate": start_date.strftime("%Y-%m-%d"),
        "toDate": end_date.strftime("%Y-%m-%d"),
        "alertlevel": "Green;Orange;Red",
        "eventlist": ";".join(event_types),  # Include all event types
        "country": ""
    }
    print(f"Fetching events from {params['fromDate']} to {params['toDate']} for types {event_types}...")
    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()

    data = response.json()
    events = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        events.append({
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
        })
    return events

def main():
    start_date = datetime(2000, 1, 1)  # Starting date
    end_date = datetime(2024, 11, 28)  # Ending date
    interval = timedelta(days=30)  # Fetch monthly
    event_types = ["EQ", "TS", "TC", "FL", "VO", "DR", "WF"]

    all_data = pd.DataFrame()
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + interval, end_date)
        try:
            events = fetch_events(current_date, next_date, event_types)
            if events:
                df = pd.DataFrame(events)
                all_data = pd.concat([all_data, df], ignore_index=True)
        except requests.RequestException as e:
            print(f"Error fetching events for {current_date.date()} to {next_date.date()}: {e}")
        current_date = next_date

    # Export data to yearly CSVs
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
