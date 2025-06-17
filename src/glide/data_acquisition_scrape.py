"""Data acquisition script for Glide Number using Selenium and BeautifulSoup."""

from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://glidenumber.net/glide/public/result/report.jsp"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"

PROFILE_PATH = (
     "/home/evangelos/snap/firefox/common/.mozilla/firefox/"
     "cf7shfvv.selenium_profile"
 )


Path("./data/glide/").mkdir(parents=True, exist_ok=True)
CSV_OUTPUT = "./data/glide/glide_events.csv"

def scrape_with_selenium() -> str:
    """Use Selenium to interact with the Glide Number website and return the rendered.

    HTML as a string.
    """
    options = FirefoxOptions()
    options.headless = False # type: ignore[attr-defined]
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)

    service = FirefoxService(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(URL)

        WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.NAME, "variables")),
        )

        variables_field = driver.find_element(By.NAME, "variables")
        for option in variables_field.find_elements(By.TAG_NAME, "option"):
            driver.execute_script("arguments[0].selected = true;", option)

        unlimited_checkbox = driver.find_element(By.NAME, "unlimited")
        if not unlimited_checkbox.is_selected():
            unlimited_checkbox.click()

        continue_button = driver.find_element(By.NAME, "continueReport")
        continue_button.click()

        WebDriverWait(driver, 60).until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "//table[@border='1' and @width='100%']//tr",
                ),
            ),
        )

        return driver.page_source

    finally:
        driver.quit()

def parse_html_to_dataframe(html: str) -> pd.DataFrame:
    """Parse the rendered HTML using BS and return the data as a DataFrame."""
    soup = BeautifulSoup(html, "html.parser")

    data_table = soup.find(
        "table",
        {
            "cellspacing": "1",
            "cellpadding": "1",
            "border": "1",
            "width": "100%",
        },
    )
    if not data_table:
        return pd.DataFrame()

    headers = [th.text.strip() for th in data_table.find_all("th")] # type: ignore[attr-defined]

    rows = []
    for tr in data_table.find_all("tr")[1:]: # type: ignore[union-attr]
        cells = [td.text.strip() for td in tr.find_all("td")] # type: ignore[attr-defined]
        # Filter out rows like "Hits:0"
        if len(cells) == len(headers) and not any("Hits:" in cell for cell in cells):
            rows.append(cells)

    return pd.DataFrame(rows, columns=headers)

if __name__ == "__main__":
    rendered_html = scrape_with_selenium()
    data_df = parse_html_to_dataframe(rendered_html)

    if not data_df.empty:
        data_df.to_csv(CSV_OUTPUT, index=False)
    else:
        pass
