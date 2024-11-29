import requests
import pandas as pd
import os
import time

SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_optimized/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_all_pages(start_date, end_date, event_type):
    all_events = []
    seen_event_ids = set()  # Track unique event IDs
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
        try:
            response = requests.get(SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Debug: Log request details
            print(f"Request URL: {response.url}")
            print(f"Response features count: {len(data.get('features', []))}")

            features = data.get("features", [])
            if not features:
                print(f"No more events found for {event_type}.")
                break

            for feature in features:
                properties = feature.get("properties", {})
                event_id = properties.get("eventid", "N/A")

                if event_id in seen_event_ids:  # Skip duplicates
                    continue

                seen_event_ids.add(event_id)
                all_events.append({
                    "event_id": event_id,
                    "event_type": properties.get("eventtype", "N/A"),
                    "event_name": properties.get("name", "N/A"),
                    "from_date": properties.get("fromdate", "N/A"),
                    "to_date": properties.get("todate", "N/A"),
                    "alert_level": properties.get("alertlevel", "N/A"),
                    "countries": ", ".join(
                        f"{c['countryname']} ({c['iso3']})"
                        for c in properties.get("affectedcountries", [])
                    ),
                    "population": properties.get("population", "N/A"),
                    "severity": properties.get("severitydata", {}).get("severity", "N/A"),
                    "alert_score": properties.get("alertscore", "N/A"),
                })

            page_number += 1
            time.sleep(1)
        except requests.RequestException as e:
            print(f"Request failed for {event_type} events page {page_number}: {e}")
            break
        except ValueError as e:
            print(f"Invalid JSON response for {event_type} events page {page_number}: {e}")
            break

    return all_events

def main():
    start_date = pd.to_datetime("2000-01-01")
    end_date = pd.to_datetime("2024-11-28")
    event_types = ["EQ", "TS", "TC", "FL", "VO", "DR", "WF"]

    all_data = []
    for event_type in event_types:
        events = fetch_all_pages(start_date, end_date, event_type)
        all_data.extend(events)

    if all_data:
        df = pd.DataFrame(all_data)
        output_file = os.path.join(OUTPUT_DIR, "gdacs_all_events.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} events to {output_file}")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
