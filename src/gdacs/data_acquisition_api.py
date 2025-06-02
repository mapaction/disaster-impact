"""GDACS Data Acquisition Script."""

import logging
import pathlib
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
OUTPUT_DIR = "./data_raw/gdacs_v2_run/"
pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def fetch_events(
    start_date: datetime,
    end_date: datetime,
    event_type: str,
) -> list[dict]:
    """Fetch GDACS events of a specific type within a date range."""
    params = {
        "fromDate": start_date.strftime("%Y-%m-%d"),
        "toDate": end_date.strftime("%Y-%m-%d"),
        "alertlevel": "Green;Orange;Red",
        "eventlist": event_type,
        "country": "",
    }

    logging.info(
        "Fetching %s events from %s to %s...",
        event_type,
        params["fromDate"],
        params["toDate"],
    )

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        if not response.text.strip():
            logging.warning(
                "Empty response body for %s events %s to %s",
                event_type,
                params["fromDate"],
                params["toDate"],
            )
            return []

        data = response.json()

        return [
            {
                "event_id": feature["properties"].get("eventid", "N/A"),
                "event_type": feature["properties"].get("eventtype", "N/A"),
                "event_name": feature["properties"].get("name", "N/A"),
                "from_date": feature["properties"].get("fromdate", "N/A"),
                "to_date": feature["properties"].get("todate", "N/A"),
                "alert_level": feature["properties"].get("alertlevel", "N/A"),
                "countries": ", ".join(
                    c["countryname"]
                    for c in feature["properties"].get("affectedcountries", [])
                ),
                "iso3": ", ".join(
                    c["iso3"]
                    for c in feature["properties"].get("affectedcountries", [])
                ),
                "location": [
                    c["countryname"]
                    for c in feature["properties"].get("affectedcountries", [])
                ],
                "population": feature["properties"].get("population", "N/A"),
                "severity": feature["properties"]
                .get("severitydata", {})
                .get("severity", "N/A"),
                "alert_score": feature["properties"].get("alertscore", "N/A"),
                "bbox": feature.get("bbox", []),
                "coordinates": feature.get("geometry", {}).get("coordinates", []),
            }
            for feature in data.get("features", [])
        ]

    except requests.exceptions.JSONDecodeError:
        logging.exception(
            "JSON decode error for %s events %s to %s first 200 chars: %r",
            event_type,
            params["fromDate"],
            params["toDate"],
            response.text[:200],
        )
        return []

    except requests.RequestException:
        logging.exception(
            "Request failed for %s events %s to %s",
            event_type,
            params["fromDate"],
            params["toDate"],
        )
        return []


def main() -> None:
    """Main function to fetch GDACS events and save them to CSV files."""
    start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 11, 28, tzinfo=timezone.utc)
    interval = timedelta(days=30)
    event_types = ["EQ", "TS", "TC", "FL", "VO", "DR", "WF"]

    all_data = pd.DataFrame()
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + interval, end_date)
        try:
            for event_type in event_types:
                events = fetch_events(current_date, next_date, event_type)
                if events:
                    events_df = pd.DataFrame(events)
                    all_data = pd.concat([all_data, events_df], ignore_index=True)
                else:
                    logging.info(
                        "No events found for %s from %s to %s",
                        event_type,
                        current_date.date(),
                        next_date.date(),
                    )
        except Exception:
            logging.exception(
                "Unexpected error occurred while processing events from %s to %s",
                current_date.date(),
                next_date.date(),
            )
        current_date = next_date

    if not all_data.empty:
        all_data["year"] = pd.to_datetime(
            all_data["from_date"],
            errors="coerce",
        ).dt.year
        for year, group in all_data.groupby("year"):
            output_file = pathlib.Path(OUTPUT_DIR) / f"gdacs_events_{year}.csv"
            group.to_csv(output_file, index=False)
            logging.info("Saved %d events to %s", len(group), output_file)
    else:
        logging.info("No data found.")


if __name__ == "__main__":
    main()
