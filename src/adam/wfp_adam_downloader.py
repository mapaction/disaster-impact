import requests
import csv
import os

API_URL = "https://services3.arcgis.com/t6lYS2Pmd8iVx1fy/ArcGIS/rest/services/ADAM_Earthquake_And_Tropical_Storm_Events/FeatureServer/1/query"
PARAMS = {
    "f": "json",
    "where": "1=1",
    "returnGeometry": "true",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "resultOffset": 0,
    "resultRecordCount": 2000
}

os.makedirs("./data/wfp_adam", exist_ok=True)
CSV_FILE = "./data/wfp_adam/adam_earthquake_events.csv"

def fetch_and_save_data():
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["OBJECTID", "country", "source", "eventid", "x", "y"])
        writer.writeheader()

        while True:
            response = requests.get(API_URL, params=PARAMS)
            data = response.json()

            if "features" not in data or not data["features"]:
                break

            for feature in data["features"]:
                attributes = feature["attributes"]
                geometry = feature.get("geometry", {})
                row = {
                    "OBJECTID": attributes.get("OBJECTID"),
                    "country": attributes.get("country"),
                    "source": attributes.get("source"),
                    "eventid": attributes.get("eventid"),
                    "x": geometry.get("x"),
                    "y": geometry.get("y")
                }
                writer.writerow(row)

            PARAMS["resultOffset"] += PARAMS["resultRecordCount"]

if __name__ == "__main__":
    fetch_and_save_data()
