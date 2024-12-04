from bs4 import BeautifulSoup
import csv

INPUT_HTML = "/home/evangelos/src/disaster-impact/debug_page.html"
OUTPUT_CSV = "glide_data_extracted.csv"

def parse_correct_table(html_file, output_csv):
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    data_table = soup.find("table", {"cellspacing": "1", "cellpadding": "1", "border": "1", "width": "100%"})
    if not data_table:
        print("Data table not found. Please inspect the HTML structure.")
        return

    headers = [th.text.strip() for th in data_table.find_all("th")]

    rows = []
    for tr in data_table.find_all("tr")[1:]:
        cells = [td.text.strip() for td in tr.find_all("td")]
        if cells:
            rows.append(cells)

    print(f"Extracted {len(rows)} rows from the target table.")

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Data successfully saved to {output_csv}")

parse_correct_table(INPUT_HTML, OUTPUT_CSV)
