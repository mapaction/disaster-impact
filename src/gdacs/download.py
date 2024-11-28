import csv
import os
from gdacs.api import GDACSAPIReader

try:
    client = GDACSAPIReader()
except Exception as e:
    print(f"Error initializing GDACSAPIReader: {e}")
    raise

os.makedirs("./data/gdacs", exist_ok=True)

disaster_types = ["TC", "EQ", "FL", "VO", "WF", "DR"]

for event_type in disaster_types:
    events_list = []  
    try:
        events = client.latest_events(event_type=event_type, limit=100)
        print(f"Fetched {len(events['features'])} events for type {event_type}")
        for feature in events["features"]:
            properties = feature["properties"]
            events_list.append({
                "event_id": properties.get("eventid"),
                "episode_id": properties.get("episodeid"),
                "event_type": event_type,
                "event_name": properties.get("eventname", "N/A"),
                "description": properties.get("description", "N/A"),
                "alert_level": properties.get("alertlevel", "N/A"),
                "country": properties.get("country", "N/A"),
                "from_date": properties.get("fromdate", "N/A"),
                "to_date": properties.get("todate", "N/A"),
                "severity": properties.get("severitydata", {}).get("severity", "N/A"),
                "severity_text": properties.get("severitydata", {}).get("severitytext", "N/A"),
            })
    except Exception as e:
        print(f"Error fetching events for {event_type}: {e}")
        continue
    try:
        output_file = f"./data/gdacs/{event_type.lower()}.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "event_id", "episode_id", "event_type", "event_name", "description",
                "alert_level", "country", "from_date", "to_date", "severity", "severity_text"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events_list)
        print(f"Saved {len(events_list)} {event_type} events to {output_file}")
    except Exception as e:
        print(f"Error writing {event_type} data to CSV: {e}")
