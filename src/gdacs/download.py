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

all_events = []

for event_type in disaster_types:
    try:
        events = client.latest_events(event_type=event_type, limit=100)
        print(f"Fetched {len(events.features)} events for type {event_type}")
        print(f"Sample event structure for {event_type}: {events}")
        
        for feature in events["features"]:
            properties = feature["properties"]
            all_events.append({
                "event_id": properties.get("event_id"),
                "episode_id": properties.get("episode_id", None),
                "event_type": event_type,
                "title": properties.get("title", "N/A"),
                "date": properties.get("fromdate", "N/A"),
                "location": properties.get("country", "N/A"),
                "magnitude": properties.get("magnitude", "N/A"),
                "alert_level": properties.get("alertlevel", "N/A"),
            })
    except Exception as e:
        print(f"Error fetching events for {event_type}: {e}")

try:
    with open("./data/gdacs/gdacs_disasters.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["event_id", "episode_id", "event_type", "title", "date", "location", "magnitude", "alert_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_events)
    print("GDACS data saved to gdacs_disasters.csv")
except Exception as e:
    print(f"Error writing to CSV: {e}")
