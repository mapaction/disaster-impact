import requests
import csv
import time
import os

base_url = "https://www.gdacs.org/gdacsapi/api/Events/geteventlist/search"

params = {
    "pageSize": 100,
    "pageNumber": 1,
}

output_dir = "./data/gdacs_suggestion_paris"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "gdacs_all_events.csv")

all_events = []

print("Fetching GDACS data...")

while True:
    print(f"Fetching page {params['pageNumber']}...")
    response = requests.get(base_url, params=params, headers={"accept": "text/plain"})
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        break

    data = response.json()
    events = data.get("features", [])

    if not events:
        print("No more events found.")
        break

    for event in events:
        properties = event.get("properties", {})
        all_events.append({
            "eventtype": properties.get("eventtype"),
            "eventid": properties.get("eventid"),
            "episodeid": properties.get("episodeid"),
            "eventname": properties.get("eventname"),
            "glide": properties.get("glide"),
            "name": properties.get("name"),
            "description": properties.get("description"),
            "alertlevel": properties.get("alertlevel"),
            "country": properties.get("country"),
            "fromdate": properties.get("fromdate"),
            "todate": properties.get("todate"),
            "iso3": properties.get("iso3"),
            "severity": properties.get("severitydata", {}).get("severity"),
        })

    print(f"Fetched {len(events)} events from page {params['pageNumber']}.")

    params["pageNumber"] += 1

    print("Waiting 1 minute before the next call...")
    time.sleep(60)

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "eventtype", "eventid", "episodeid", "eventname", "glide", "name",
        "description", "alertlevel", "country", "fromdate", "todate", "iso3", "severity"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_events)

print(f"Saved {len(all_events)} events to {output_file}")
