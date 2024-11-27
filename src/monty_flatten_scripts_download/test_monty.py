import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

base_url = "https://monty-api.ifrc.org/data/JSON"

api_token = os.getenv("MONTY_API_TOKEN")

params = {
    "Mtoken": api_token,
    "sdate": "2024-11-28",
}

response = requests.get(base_url, params=params)

if response.status_code == 200:
    data = response.json()
    
    impact_data_0 = data.get("impact_Data", [])[119]
    
    if impact_data_0:
        os.makedirs("json", exist_ok=True)
        with open("json/impact_data_0.json", "w") as json_file:
            json.dump(impact_data_0, json_file, indent=4)
        print("impact_Data[0] saved to 'json/impact_data_0.json'.")
    else:
        print("No impact_Data[0] found in the response.")
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
