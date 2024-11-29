# original script

import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://glidenumber.net/glide/public/search/details.jsp"
LAST_RECORD = 8311
CSV_FILE = "glide_data.csv"

def scrape_glide_data():
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = None
        fields = set(["Record", "GLIDE"])

        for record in range(1, LAST_RECORD + 1):
            try:
                params = {"record": record, "last": LAST_RECORD}
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                glide_id = None
                docid_input = soup.find("input", {"name": "docid"})
                if docid_input:
                    glide_id = docid_input.get("value", None)

                details = soup.find_all("tr")
                data = {"Record": record, "GLIDE": glide_id}

                for row in details:
                    cells = row.find_all("td")
                    if len(cells) == 2:
                        key = cells[0].get_text(strip=True).replace(":", "").replace(" ", "_")
                        value = cells[1].get_text(strip=True)
                        data[key] = value
                        fields.add(key)

                if writer is None:
                    writer = csv.DictWriter(file, fieldnames=list(fields))
                    writer.writeheader()

                writer.writerow(data)
                print(f"Record {record} saved with GLIDE {glide_id}.")
                
                time.sleep(1)
            
            except Exception as e:
                print(f"Error with record {record}: {e}")

if __name__ == "__main__":
    scrape_glide_data()
