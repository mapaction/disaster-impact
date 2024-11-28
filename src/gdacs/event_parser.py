import csv
import feedparser
import requests
from datetime import datetime
import os

RSS_URL = 'https://www.gdacs.org/xml/rss.xml'
EVENT_DETAILS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventdata?eventtype={event_type}&eventid={event_id}"
OUTPUT_DIR = "./data/gdacs/"
ALERT_LEVELS = ['Red', 'Orange', 'Green']

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_latest_rss_events(alert_levels=None):
    feed = feedparser.parse(RSS_URL)
    if alert_levels:
        filtered_events = [entry for entry in feed.entries if any(alert in entry.title for alert in alert_levels)]
    else:
        filtered_events = feed.entries
    return filtered_events

def fetch_event_details(event_type, event_id):
    url = EVENT_DETAILS_URL.format(event_type=event_type, event_id=event_id)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_events_to_csv(events, file_path):
    fieldnames = [
        "event_id", "event_type", "title", "summary", "link", "published_date",
        "name", "from_date", "to_date", "alert_level", "countries", "population",
        "max_wind_speed", "max_storm_surge", "vulnerability", "gdacs_score"
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

def main():
    print("Fetching latest GDACS events...")
    rss_events = fetch_latest_rss_events(ALERT_LEVELS)
    print(f"Found {len(rss_events)} events in RSS feed.")

    all_events = []

    for rss_event in rss_events:
        try:
            event_id = rss_event.link.split('eventid=')[-1]
            event_type = rss_event.link.split('eventtype=')[-1].split('&')[0].upper()

            print(f"Processing Event: {rss_event.title} (ID: {event_id}, Type: {event_type})")

            event_details = fetch_event_details(event_type, event_id)
            props = event_details.get("properties", {})
            countries = [
                f"{country['countryname']} ({country['iso3']})"
                for country in props.get("affectedcountries", [])
            ]

            all_events.append({
                "event_id": event_id,
                "event_type": event_type,
                "title": rss_event.title,
                "summary": rss_event.summary,
                "link": rss_event.link,
                "published_date": rss_event.published,
                "name": props.get("name", "N/A"),
                "from_date": props.get("fromdate", "N/A"),
                "to_date": props.get("todate", "N/A"),
                "alert_level": props.get("alertlevel", "N/A"),
                "countries": ", ".join(countries),
                "population": props.get("population", "N/A"),
                "max_wind_speed": props.get("maxwindspeed", "N/A"),
                "max_storm_surge": props.get("maxstormsurge", "N/A"),
                "vulnerability": props.get("vulnerability", "N/A"),
                "gdacs_score": props.get("alertscore", "N/A"),
            })
        except requests.RequestException as e:
            print(f"Error fetching details for event ID {event_id}: {e}")
            continue

    output_file = os.path.join(OUTPUT_DIR, "gdacs_events.csv")
    save_events_to_csv(all_events, output_file)
    print(f"Saved {len(all_events)} events to {output_file}")

if __name__ == "__main__":
    main()
