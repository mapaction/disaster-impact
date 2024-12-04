from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

URL = "https://glidenumber.net/glide/public/result/report.jsp"
OUTPUT_CSV = "glide_data_final.csv"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"
PROFILE_PATH = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"

def scrape_glide_data():
    firefox_options = FirefoxOptions()
    firefox_options.headless = False
    firefox_options.add_argument("-profile")
    firefox_options.add_argument(PROFILE_PATH)

    firefox_service = FirefoxService(GECKODRIVER_PATH, timeout=300)
    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

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
        print("Form submitted.")

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//table[@border='1' and @width='100%']"))
        )
        print("Table loaded successfully.")

        table = driver.find_element(By.XPATH, "//table[@border='1' and @width='100%']")
        rows = table.find_elements(By.TAG_NAME, "tr")
        headers = [header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, "th")]

        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                data.append([cell.text.strip() for cell in cells])

        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"Data successfully saved to {OUTPUT_CSV}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_glide_data()
