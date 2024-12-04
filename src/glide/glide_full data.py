import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://glidenumber.net/glide/public/result/report.jsp"
OUTPUT_CSV = "glide_full_data_debug.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://glidenumber.net/glide/public/search/search.jsp",
    "Origin": "https://glidenumber.net",
}

COOKIES = {
    "JSESSIONID": "295648B26E9FC2A084A8C0B8093BB930",
}

PAYLOAD_TEMPLATE = {
    "variables": "all",
    "unlimited": "on",
    "page": "1",
    "continueReport": "true",
}

TOTAL_PAGES = 832

def fetch_page_data(page_number):
    print(f"\nFetching page {page_number} of {TOTAL_PAGES}...")
    payload = PAYLOAD_TEMPLATE.copy()
    payload["page"] = str(page_number)

    try:
        response = requests.post(BASE_URL, headers=HEADERS, cookies=COOKIES, data=payload, timeout=30)
        response.raise_for_status()
        print(f"Page {page_number} fetched successfully.")
        print(f"Response preview:\n{response.text[:500]}")
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        return None

def parse_table_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", {"border": "1", "width": "100%"})

    if not table:
        print("No table found on this page.")
        print(f"HTML content preview:\n{html_content[:1000]}")
        return [], []

    print(f"Table HTML preview:\n{table.prettify()[:500]}")

    headers = [th.text.strip() for th in table.find_all("th")]

    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.text.strip() for td in tr.find_all("td")]
        rows.append(cells)

    print(f"Extracted {len(rows)} rows from the table.")
    return headers, rows

def scrape_all_pages():
    headers, all_data = None, []
    for page_number in range(1, TOTAL_PAGES + 1):
        html_content = fetch_page_data(page_number)
        if not html_content:
            print(f"Stopping at page {page_number} due to an error or empty response.")
            break

        page_headers, page_data = parse_table_from_html(html_content)
        if not page_data:
            print(f"No data found on page {page_number}. Stopping.")
            break

        if headers is None:
            headers = page_headers

        all_data.extend(page_data)

    if headers and all_data:
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(all_data)
        print(f"Data successfully saved to {OUTPUT_CSV}")
    else:
        print("No data to save. Please check the debug output.")

if __name__ == "__main__":
    scrape_all_pages()
