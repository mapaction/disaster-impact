import csv
import os
from gdacs.api import GDACSAPIReader

# Initialize the GDACS API Client
try:
    client = GDACSAPIReader()
except Exception as e:
    print(f"Error initializing GDACSAPIReader: {e}")
    raise

# Ensure output directory exists
os.makedirs("./data/csv", exist_ok=True)

# Define disaster types
disaster_types = ["TC", "EQ", "FL", "VO", "WF", "DR"]

# Fetch all events and save them
all_events = []

for event_type in disaster_types:
    try:
        events = client.latest_events(event_type=event_type, limit=100)  # Adjust limit as needed
        print(f"Fetched {len(events)} events for type {event_type}")
        for event in events:
            all_events.append({
                "event_id": event.get("event_id"),
                "episode_id": event.get("episode_id"),
                "event_type": event_type,
                "title": event.get("title"),
                "date": event.get("fromdate"),
                "location": event.get("country"),
                "magnitude": event.get("magnitude"),
                "alert_level": event.get("alertlevel"),
            })
    except Exception as e:
        print(f"Error fetching events for {event_type}: {e}")

# Save to CSV
try:
    with open("./data/csv/gdacs_disasters.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["event_id", "episode_id", "event_type", "title", "date", "location", "magnitude", "alert_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_events)
    print("GDACS data saved to gdacs_disasters.csv")
except Exception as e:
    print(f"Error writing to CSV: {e}")
