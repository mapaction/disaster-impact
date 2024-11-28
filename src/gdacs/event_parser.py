import requests
import csv
import os

EVENT_LIST_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/EVENTS4APP"
EVENT_DETAILS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventdata?eventtype={event_type}&eventid={event_id}"
OUTPUT_DIR = "./data/gdacs/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch paginated events from the event list API
def fetch_events_with_offset(offset):
    url = EVENT_LIST_URL.format(offset=offset)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_event_details(event_type, event_id):
    url = EVENT_DETAILS_URL.format(event_type=event_type, event_id=event_id)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_events_to_csv(events, file_path):
    fieldnames = [
        "event_id", "event_type", "event_name", "from_date", "to_date",
        "alert_level", "countries", "population", "max_wind_speed",
        "max_storm_surge", "vulnerability", "gdacs_score"
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

def main():
    print("Fetching all GDACS events with pagination...")
    all_events = []
    offset = 0
    batch_size = 100

    while True:
        events_data = fetch_events_with_offset(offset)
        features = events_data.get("features", [])

        if not features:
            print("No more events found.")
            break

        print(f"Fetched {len(features)} events starting from offset {offset}")

        for event in features:
            props = event.get("properties", {})
            event_id = props.get("eventid")
            event_type = props.get("eventtype")

            print(f"Processing Event ID: {event_id}, Type: {event_type}")

            try:
                event_details = fetch_event_details(event_type, event_id)
                details_props = event_details.get("properties", {})
                countries = [
                    f"{country['countryname']} ({country['iso3']})"
                    for country in details_props.get("affectedcountries", [])
                ]

                all_events.append({
                    "event_id": event_id,
                    "event_type": event_type,
                    "event_name": details_props.get("name", "N/A"),
                    "from_date": details_props.get("fromdate", "N/A"),
                    "to_date": details_props.get("todate", "N/A"),
                    "alert_level": details_props.get("alertlevel", "N/A"),
                    "countries": ", ".join(countries),
                    "population": details_props.get("population", "N/A"),
                    "max_wind_speed": details_props.get("maxwindspeed", "N/A"),
                    "max_storm_surge": details_props.get("maxstormsurge", "N/A"),
                    "vulnerability": details_props.get("vulnerability", "N/A"),
                    "gdacs_score": details_props.get("alertscore", "N/A"),
                })
            except requests.RequestException as e:
                print(f"Error fetching details for Event ID {event_id}: {e}")
                continue

        offset += batch_size  # Move to the next batch

    # Save all events to CSV
    output_file = os.path.join(OUTPUT_DIR, "gdacs_all_events.csv")
    save_events_to_csv(all_events, output_file)
    print(f"Saved {len(all_events)} events to {output_file}")

if __name__ == "__main__":
    main()
