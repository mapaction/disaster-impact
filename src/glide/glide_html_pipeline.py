from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

URL = "https://glidenumber.net/glide/public/result/report.jsp"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"
PROFILE_PATH = "/home/evangelos/snap/firefox/common/.mozilla/firefox/cf7shfvv.selenium_profile"
CSV_OUTPUT = "./data/glide/glide_data_combined_all.csv"

def scrape_with_selenium():
    options = FirefoxOptions()
    options.headless = False
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)

    service = FirefoxService(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

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
        print("Form submitted. Waiting for data to load...")

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//table[@border='1' and @width='100%']//tr"))
        )
        print("Data table detected.")

        return driver.page_source

    finally:
        driver.quit()

def parse_html_to_dataframe(html):
    """
    Parse the rendered HTML using BeautifulSoup and return the data as a DataFrame.
    """
    from bs4 import BeautifulSoup
    import pandas as pd

    soup = BeautifulSoup(html, "html.parser")

    data_table = soup.find("table", {"cellspacing": "1", "cellpadding": "1", "border": "1", "width": "100%"})
    if not data_table:
        print("Data table not found in the HTML.")
        return pd.DataFrame()

    headers = [th.text.strip() for th in data_table.find_all("th")]

    rows = []
    for tr in data_table.find_all("tr")[1:]:
        cells = [td.text.strip() for td in tr.find_all("td")]
        # Filter out rows like "Hits:0" (rows with fewer cells than headers or unexpected content)
        if len(cells) == len(headers) and not any("Hits:" in cell for cell in cells):
            rows.append(cells)

    print(f"Extracted {len(rows)} rows from the table.")

    return pd.DataFrame(rows, columns=headers)

if __name__ == "__main__":
    rendered_html = scrape_with_selenium()
    data_df = parse_html_to_dataframe(rendered_html)

    if not data_df.empty:
        data_df.to_csv(CSV_OUTPUT, index=False)
        print(f"Data successfully saved to {CSV_OUTPUT}")
    else:
        print("No data found to save.")
