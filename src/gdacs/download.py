import csv
import os
from gdacs.api import GDACSAPIReader

try:
    client = GDACSAPIReader()
except Exception as e:
    print(f"Error initializing GDACSAPIReader: {e}")
    raise

os.makedirs("./data/csv", exist_ok=True)

disaster_types = ["TC", "EQ", "FL", "VO", "WF", "DR"]

all_events = []

for event_type in disaster_types:
    try:
        events = client.latest_events(event_type=event_type, limit=100)
        print(f"Fetched {len(events)} events for type {event_type}")
        for event in events:
            event_id, episode_id, title, fromdate, country, magnitude, alertlevel = event
            all_events.append({
                "event_id": event_id,
                "episode_id": episode_id,
                "event_type": event_type,
                "title": title,
                "date": fromdate,
                "location": country,
                "magnitude": magnitude,
                "alert_level": alertlevel,
            })
    except Exception as e:
        print(f"Error fetching events for {event_type}: {e}")

try:
    with open("./data/csv/gdacs_disasters.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["event_id", "episode_id", "event_type", "title", "date", "location", "magnitude", "alert_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_events)
    print("GDACS data saved to gdacs_disasters.csv")
except Exception as e:
    print(f"Error writing to CSV: {e}")
