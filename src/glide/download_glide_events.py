import requests
from bs4 import BeautifulSoup
import csv
import time
import os

BASE_URL = "https://glidenumber.net/glide/public/search/search.jsp"
os.makedirs("./data/glide", exist_ok=True)
CSV_FILE = "./data/glide/glide_events_cleaned.csv"
FIELDS = ["GLIDE Number", "Event Type", "Country", "Comments"]

def fetch_page_data(page, processed_ids):
    try:
        params = {"page": page}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"cellspacing": "1", "border": "1", "width": "100%"})
        if not table:
            print(f"No table found on page {page}")
            return []

        rows = table.find_all("tr", class_="bgLightLight")
        data = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                glide_number = cells[0].get_text(strip=True)
                if glide_number not in processed_ids:
                    entry = {
                        "GLIDE Number": glide_number,
                        "Event Type": cells[1].get_text(strip=True),
                        "Country": cells[2].get_text(strip=True),
                        "Comments": cells[3].get_text(strip=True),
                    }
                    data.append(entry)
                    processed_ids.add(glide_number)

        return data

    except Exception as e:
        print(f"Error fetching data for page {page}: {e}")
        return []

def scrape_all_pages():
    processed_ids = set()
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for page in range(1, 334):
            print(f"Fetching page {page}...")
            data = fetch_page_data(page, processed_ids)
            writer.writerows(data)
            time.sleep(1)

    print(f"Total unique entries written: {len(processed_ids)}")
    if len(processed_ids) == 8312:
        print("Success: The total matches the expected count.")
    else:
        print(f"Discrepancy: Expected 8312, but got {len(processed_ids)}")

if __name__ == "__main__":
    scrape_all_pages()
