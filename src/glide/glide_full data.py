import requests
from bs4 import BeautifulSoup
import csv

url = "https://glidenumber.net/glide/public/result/report.jsp"

form_data = {
    "variables": [
        "disasters.sEventId || '-' || sGlide || '-' || sLocationCode as GLIDE_number",
        "sEventName as Event",
        "geography.sLocation as Country",
        "(CAST(nyear as varchar(8)) || '/' || CAST(nmonth as varchar(8)) || '/' || CAST(nday as varchar(8))) as Date_",
    ],
    "unlimited": "Y",
    "continueReport": "Continue"
}

session = requests.Session()

response = session.post(url, data=form_data)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"border": "1", "width": "100%"})
    if table:
        headers_row = table.find("tr")
        headers = [header.text.strip() for header in headers_row.find_all("th")]

        data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if cells:
                data.append([cell.text.strip() for cell in cells])

        output_file = "./data/glide/glide_data_all.csv"
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)

        print(f"Data successfully saved to {output_file}")
    else:
        print("Data table not found.")
else:
    print(f"Failed to retrieve the data. Status code: {response.status_code}")
