import requests
import csv
import time
import os
from datetime import datetime, timedelta

base_url = "https://www.gdacs.org/gdacsapi/api/Events/geteventlist/search"

params = {
    "pageSize": 100,
    "pageNumber": 1,
    "fromDate": "2000-01-01T00:00:00",
    "toDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
}

output_dir = "./data/gdacs_suggestion_paris"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "gdacs_all_events.csv")

all_events = []
date_step = timedelta(days=30)
start_date = datetime.strptime(params["fromDate"], "%Y-%m-%dT%H:%M:%S")
end_date = datetime.strptime(params["toDate"], "%Y-%m-%dT%H:%M:%S")
current_start = start_date

print("Fetching GDACS data...")

while current_start < end_date:
    current_end = min(current_start + date_step, end_date)
    params["fromDate"] = current_start.strftime("%Y-%m-%dT%H:%M:%S")
    params["toDate"] = current_end.strftime("%Y-%m-%dT%H:%M:%S")

    params["pageNumber"] = 1
    while True:
        print(f"Fetching page {params['pageNumber']} for range {params['fromDate']} to {params['toDate']}...")
        response = requests.get(base_url, params=params, headers={"accept": "text/plain"})

        if response.status_code == 204:
            print("No more events found (204 No Content).")
            break
        elif response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response content: {response.text}")
            break

        data = response.json()
        events = data.get("features", [])

        if not events:
            print("No more events found in this range.")
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

    current_start = current_end + timedelta(seconds=1)

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "eventtype", "eventid", "episodeid", "eventname", "glide", "name",
        "description", "alertlevel", "country", "fromdate", "todate", "iso3", "severity"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_events)

print(f"Saved {len(all_events)} events to {output_file}")
