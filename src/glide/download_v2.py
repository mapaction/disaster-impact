from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import time

BASE_URL = "https://glidenumber.net/glide/public/search/search.jsp"
CSV_FILE = "./data/glide/glide_events_cleaned2.csv"
FIELDS = ["GLIDE Number", "Event Type", "Country", "Comments"]
profile_path = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"

def fetch_all_pages():
    os.makedirs("./data/glide", exist_ok=True)
    processed_ids = set()
    total_pages = 333  # Define the total number of pages based on your observation

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        firefox_options = FirefoxOptions()
        firefox_options.headless = True  # Enable headless mode
        firefox_options.add_argument("-profile")
        firefox_options.add_argument(profile_path)

        firefox_service = FirefoxService("/usr/local/bin/geckodriver", timeout=300)
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

        try:
            driver.get(BASE_URL)
            current_offset = 0

            for page in range(1, total_pages + 1):
                try:
                    # Wait for the table to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//table[@cellspacing='1']"))
                    )

                    # Extract table data
                    table = driver.find_element(By.XPATH, "//table[@cellspacing='1']")
                    rows = table.find_elements(By.XPATH, ".//tr[@class='bgLightLight']")

                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 4:
                            glide_number = cells[0].text.strip()
                            if glide_number not in processed_ids:
                                entry = {
                                    "GLIDE Number": glide_number,
                                    "Event Type": cells[1].text.strip(),
                                    "Country": cells[2].text.strip(),
                                    "Comments": cells[3].text.strip(),
                                }
                                writer.writerow(entry)
                                processed_ids.add(glide_number)

                    # Locate the "Next" button using the current offset
                    current_offset += 25
                    next_button = driver.find_element(By.XPATH, f"//a[@href='javascript:submitForm({current_offset})']")

                    # Click the "Next" button and wait for the next page to load
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)

                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    break

        finally:
            driver.quit()

    print(f"Total unique entries written: {len(processed_ids)}")

if __name__ == "__main__":
    fetch_all_pages()
