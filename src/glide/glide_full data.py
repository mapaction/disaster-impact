from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

URL = "https://glidenumber.net/glide/public/result/report.jsp"
OUTPUT_CSV = "glide_data_full_debugged.csv"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"
PROFILE_PATH = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"

def debug_save_page_source(driver, filename="debug_page.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"Page source saved to {filename}")

def wait_for_table_to_load(driver, timeout=60):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//table[@border='1' and @width='100%']//tr"))
    )
    print("Table detected and initial rows loaded.")

def scroll_to_load_all_rows(driver, table_xpath, max_scroll_attempts=50):
    table = driver.find_element(By.XPATH, table_xpath)
    prev_height = 0
    for attempt in range(max_scroll_attempts):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", table)
        time.sleep(2)
        current_height = driver.execute_script("return arguments[0].scrollHeight", table)
        if current_height == prev_height:
            print(f"Scrolling complete after {attempt + 1} attempts.")
            break
        prev_height = current_height
    print("Finished scrolling through the table.")

def extract_table_data(driver):
    table = driver.find_element(By.XPATH, "//table[@border='1' and @width='100%']")
    rows = table.find_elements(By.TAG_NAME, "tr")

    with open("debug_table.html", "w", encoding="utf-8") as debug_file:
        debug_file.write(table.get_attribute("outerHTML"))
    print("Saved table HTML for debugging.")

    headers = [header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, "th")]

    data = []
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            data.append([cell.text.strip() for cell in cells])

    print(f"Extracted {len(data)} rows from the table.")
    return headers, data

def scrape_glide_data():
    options = FirefoxOptions()
    options.headless = False
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)

    firefox_service = FirefoxService(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=firefox_service, options=options)

    try:
        driver.get(URL)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "variables"))
        )
        print("Form loaded successfully.")

        variables_field = driver.find_element(By.NAME, "variables")
        for option in variables_field.find_elements(By.TAG_NAME, "option"):
            driver.execute_script("arguments[0].selected = true;", option)
        print("All variables selected.")

        unlimited_checkbox = driver.find_element(By.NAME, "unlimited")
        if not unlimited_checkbox.is_selected():
            unlimited_checkbox.click()
        print("Unlimited results checkbox selected.")

        continue_button = driver.find_element(By.NAME, "continueReport")
        continue_button.click()
        print("Form submitted. Waiting for table to load...")

        wait_for_table_to_load(driver)

        table_xpath = "//table[@border='1' and @width='100%']"
        scroll_to_load_all_rows(driver, table_xpath)

        headers, data = extract_table_data(driver)

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"Data successfully saved to {OUTPUT_CSV}")

    finally:
        debug_save_page_source(driver)
        driver.quit()

if __name__ == "__main__":
    scrape_glide_data()
