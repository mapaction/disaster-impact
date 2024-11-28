import requests
import csv
import os

# Constants
SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data/gdacs_search/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Parameters for the API request
PARAMS = {
    "fromDate": "2000-1-1",  # Adjust dates as needed
    "toDate": "2024-11-28",
    "alertlevel": "Green;Orange;Red",  # Include all alert levels
    "eventlist": "EQ;TS;TC;FL;VO;DR;WF",  # Earthquakes, Tropical Cyclones, Floods, etc.
    "country": ""  # Empty to include all countries
}

# Save events to CSV
def save_to_csv(events, output_file):
    fieldnames = [
        "event_id", "event_type", "event_name", "from_date", "to_date",
        "alert_level", "countries", "population", "severity", "alert_score"
    ]
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

# Fetch and parse events
def fetch_events(params):
    print(f"Fetching events from {params['fromDate']} to {params['toDate']}...")
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
    try:
        events = fetch_events(PARAMS)
        output_file = os.path.join(OUTPUT_DIR, f"gdacs_events_{PARAMS['fromDate']}_to_{PARAMS['toDate']}.csv")
        save_to_csv(events, output_file)
        print(f"Saved {len(events)} events to {output_file}")
    except requests.RequestException as e:
        print(f"Error fetching events: {e}")

if __name__ == "__main__":
    main()
