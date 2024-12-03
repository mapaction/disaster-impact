from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Constants
URL = "https://glidenumber.net/glide/public/result/report.jsp"
OUTPUT_CSV = "glide_full_data.csv"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"
PROFILE_PATH = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"

def select_all_options(driver, select_name):
    """
    Select all options in a dropdown field.
    """
    try:
        select_element = driver.find_element(By.NAME, select_name)
        options = select_element.find_elements(By.TAG_NAME, "option")
        for option in options:
            driver.execute_script("arguments[0].selected = true;", option)  # Ensure option is selected
        print(f"Selected all options in {select_name}.")
    except Exception as e:
        print(f"Failed to select options in {select_name}: {e}")

def scrape_table(driver, table_xpath):
    """
    Scrape the visible table on the page.
    """
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )
        table = driver.find_element(By.XPATH, table_xpath)
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Extract headers
        headers = [header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, "th")]

        # Extract rows
        data = []
        for row in rows[1:]:  # Skip headers
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                data.append([cell.text.strip() for cell in cells])
        
        return headers, data
    except Exception as e:
        print(f"Failed to scrape the table: {e}")
        return [], []

def scrape_glide_table():
    """
    Main function to scrape the GLIDE table.
    """
    firefox_options = FirefoxOptions()
    firefox_options.headless = False  # Set to True for headless mode
    firefox_options.add_argument("-profile")
    firefox_options.add_argument(PROFILE_PATH)

    firefox_service = FirefoxService(GECKODRIVER_PATH, timeout=300)
    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

    try:
        driver.get(URL)

        # Wait for the form to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "variables"))
        )

        # Select all options in the "variables" dropdown
        select_all_options(driver, "variables")

        # Check the "Unlimited results" checkbox
        try:
            unlimited_checkbox = driver.find_element(By.NAME, "unlimited")
            if not unlimited_checkbox.is_selected():
                unlimited_checkbox.click()
            print("Checked the 'Unlimited results' checkbox.")
        except Exception as e:
            print(f"Failed to check 'Unlimited results' checkbox: {e}")

        # Submit the form
        try:
            continue_button = driver.find_element(By.NAME, "continueReport")
            continue_button.click()
            print("Clicked the 'Continue' button.")
        except Exception as e:
            print(f"Failed to click 'Continue' button: {e}")

        # Scrape the table
        table_xpath = "//table[@border='1' and @width='100%']"
        headers, data = scrape_table(driver, table_xpath)

        # Save data to CSV
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers)  # Write headers
            writer.writerows(data)  # Write rows
        print(f"Data successfully saved to {OUTPUT_CSV}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_glide_table()
