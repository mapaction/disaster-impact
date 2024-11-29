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
CSV_FILE = "./data/glide/glide_events_cleaned3.csv"
FIELDS = ["GLIDE Number", "Event Type", "Country", "Comments"]
profile_path = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"

def fetch_all_pages():
    os.makedirs("./data/glide", exist_ok=True)
    processed_ids = set()

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
            reached_last_page = False

            while True:
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

                    # Navigation Logic
                    if not reached_last_page:
                        try:
                            current_offset += 25
                            print(f"Current offset: {current_offset}")

                            # Navigate to the next or last page
                            if current_offset == 8250:
                                print("Switching to the 'Last' button.")
                                last_button = driver.find_element(By.XPATH, "//a[img[@src='/glide/images/arrow-last.gif']]")
                                driver.execute_script("arguments[0].click();", last_button)
                                reached_last_page = True
                            else:
                                next_button = driver.find_element(By.XPATH, f"//a[@href='javascript:submitForm({current_offset})']")
                                driver.execute_script("arguments[0].click();", next_button)

                            time.sleep(3)
                        except Exception as e:
                            print(f"Error navigating forward: {e}")
                            break
                    else:
                        # Scrape reverse navigation links
                        print("Scraping in reverse order.")
                        try:
                            reverse_links = [
                                {"offset": 8300, "page": "333"},
                                {"offset": 8275, "page": "332"},
                                {"offset": 8250, "page": "331"},
                            ]

                            for reverse in reverse_links:
                                print(f"Navigating to page {reverse['page']} with offset {reverse['offset']}")
                                reverse_button = driver.find_element(
                                    By.XPATH, f"//a[@href='javascript:submitForm({reverse['offset']})']"
                                )
                                driver.execute_script("arguments[0].click();", reverse_button)
                                time.sleep(3)

                                # Re-scrape the data for the reverse page
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//table[@cellspacing='1']"))
                                )

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

                            break  # Exit after reverse scraping
                        except Exception as e:
                            print(f"Error during reverse navigation: {e}")
                            break

                except Exception as e:
                    print(f"Error during scraping: {e}")
                    break

        finally:
            driver.quit()

    print(f"Total unique entries written: {len(processed_ids)}")

if __name__ == "__main__":
    fetch_all_pages()
