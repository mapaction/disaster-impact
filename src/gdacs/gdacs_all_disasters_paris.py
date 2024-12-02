import requests
import pandas as pd
import os
import time
from collections import Counter

SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_suggestions_paris/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_events(params):
    """
    Fetch events from the GDACS API with the given parameters.
    """
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def analyze_page_content(features):
    """
    Analyze the distribution of event types in the current page.
    """
    event_types = [feature.get("properties", {}).get("eventtype", "N/A") for feature in features]
    return Counter(event_types)

def fetch_all_events(start_date, end_date):
    """
    Fetch all events dynamically by analyzing event type distributions per page.
    """
    all_events = []
    seen_event_ids = set()
    page_number = 1

    event_types_to_query = {"EQ", "TS", "TC", "FL", "VO", "DR", "WF"}  # Start with all
    remaining_event_types = set(event_types_to_query)

    while remaining_event_types:
        print(f"Querying event types: {remaining_event_types}")
        params = {
            "fromDate": start_date.strftime("%Y-%m-%d"),
            "toDate": end_date.strftime("%Y-%m-%d"),
            "alertlevel": "Green;Orange;Red",
            "eventlist": ";".join(remaining_event_types),
            "pageSize": 100,
            "pageNumber": page_number,
        }
        print(f"Fetching page {page_number} for {remaining_event_types}...")
        data = fetch_events(params)
        features = data.get("features", [])
        
        if not features:
            print("No more events found for this query.")
            break

        distribution = analyze_page_content(features)
        print(f"Event type distribution: {distribution}")

        for feature in features:
            props = feature.get("properties", {})
            event_id = props.get("eventid", "N/A")
            if event_id not in seen_event_ids:
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

        # Remove dominant event types for further queries
        for event_type, count in distribution.items():
            if count >= 100:
                remaining_event_types.discard(event_type)

        page_number += 1
        time.sleep(1)

    return all_events

def main():
    start_date = pd.to_datetime("2000-01-01")
    end_date = pd.to_datetime("2024-11-28")

    print("Fetching all disaster events dynamically...")
    all_events = fetch_all_events(start_date, end_date)

    if all_events:
        df = pd.DataFrame(all_events)
        output_file = os.path.join(OUTPUT_DIR, "gdacs_all_disasters_dynamic.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} events to {output_file}")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
