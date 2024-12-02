import requests
import pandas as pd
import os
import time

SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_suggestions_paris/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_events(params):
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def fetch_all_events(start_date, end_date, event_type):
    """
    Fetch all events for a specific event type with pagination.
    """
    all_events = []
    seen_event_ids = set()
    page_number = 1

    while True:
        params = {
            "fromDate": start_date.strftime("%Y-%m-%d"),
            "toDate": end_date.strftime("%Y-%m-%d"),
            "alertlevel": "Green;Orange;Red",
            "eventlist": event_type,
            "pageSize": 100,
            "pageNumber": page_number,
        }
        print(f"Fetching {event_type} events: page {page_number} from {params['fromDate']} to {params['toDate']}...")
        data = fetch_events(params)
        features = data.get("features", [])

        if not features:
            print(f"No more events found for {event_type}.")
            break

        for feature in features:
            props = feature.get("properties", {})
            event_id = props.get("eventid", "N/A")
            if event_id not in seen_event_ids:  # Avoid duplicates
                seen_event_ids.add(event_id)
                all_events.append({
                    "event_id": event_id,
                    "event_type": props.get("eventtype", "N/A"),
                    "event_name": props.get("name", "N/A"),
                    "from_date": props.get("fromdate", "N/A"),
                    "to_date": props.get("todate", "N/A"),
                    "alert_level": props.get("alertlevel", "N/A"),
                    "countries": ", ".join(
                        f"{c['countryname']} ({c['iso3']})"
                        for c in props.get("affectedcountries", [])
                    ),
                    "population": props.get("population", "N/A"),
                    "severity": props.get("severitydata", {}).get("severity", "N/A"),
                    "alert_score": props.get("alertscore", "N/A"),
                })

        page_number += 1
        time.sleep(1)  # Avoid rate-limiting

    return all_events

def main():
    start_date = pd.to_datetime("2000-01-01")
    end_date = pd.to_datetime("2024-11-28")
    event_types = ["EQ", "TS", "TC", "FL", "VO", "DR", "WF"]

    all_data = []
    for event_type in event_types:
        print(f"Fetching events for type: {event_type}")
        events = fetch_all_events(start_date, end_date, event_type)
        all_data.extend(events)

    if all_data:
        df = pd.DataFrame(all_data)
        output_file = os.path.join(OUTPUT_DIR, "gdacs_all_disasters_refined.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} events to {output_file}")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
