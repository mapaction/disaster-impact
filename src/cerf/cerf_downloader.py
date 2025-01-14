import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = 'https://cerf.un.org/what-we-do/allocation/all/emergency/'
DETAILS_BASE_URL = 'https://cerf.un.org/what-we-do/allocation/'

def fetch_emergency_list():
    cerf_url = 'https://cerf.un.org/fundingByEmergency/all'
    response = requests.get(cerf_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching CERF emergency list: {response.status_code}")
        return []

def clean_text(cell):
    return cell.get_text(separator=' ').strip()

def clean_approved_amount(amount):
    """ Remove 'US$' and commas from approved_amount field and return as a number string """
    return amount.replace('US$', '').replace('US $', '').replace(',', '').strip()

def clean_date_format(date_text):
    """ Reformat date from 'DD MMM YYYY' to 'DD/MM/YYYY' """
    try:
        return datetime.strptime(date_text, "%d %b %Y").strftime("%d/%m/%Y")
    except ValueError:
        return date_text  # Keep as-is if it doesn't match expected format

def fetch_project_details(allocation_code, project_code, year, emergency_id):
    """
    Dynamically build the link for each project and scrape additional details.
    """
    details_url = f"{DETAILS_BASE_URL}{year}/emergency/{emergency_id}/{allocation_code}/{project_code}"
    response = requests.get(details_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrape the 'Group(s) of people targeted' if available
        groups_targeted_element = soup.find('div', string="Group(s) of people targeted")
        groups_targeted = groups_targeted_element.find_next('div').text.strip() if groups_targeted_element else "N/A"

        # Scrape the 'Number of people targeted' if available
        number_of_people_element = soup.find('div', string="Number of people targeted")
        number_of_people = number_of_people_element.find_next('div').text.strip() if number_of_people_element else "N/A"

        # Scrape the 'Implementation dates' if available
        implementation_dates_element = soup.find('div', string="Implementation dates")
        if implementation_dates_element:
            implementation_dates = implementation_dates_element.find_next('div').text.strip()
            implementation_dates = implementation_dates.replace("\n", " | ").replace("Project start:", "Start:").replace("Project end:", "End:")
        else:
            implementation_dates = "N/A"
            
        return {
            'groups_targeted': groups_targeted,
            'number_of_people_targeted': number_of_people,
            'implementation_dates': implementation_dates
        }
    
    else:
        print(f"Error fetching project details from {details_url}: {response.status_code}")
        return {
            'groups_targeted': 'N/A',
            'number_of_people_targeted': 'N/A',
            'implementation_dates': 'N/A'
        }

def fetch_emergency_details(link_id):
    url = f'{BASE_URL}{link_id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        year_range_element = soup.find('div', {'class': 'field--name-field-year'})
        year_range = year_range_element.text.strip() if year_range_element else 'Unknown'

        total_amount_element = soup.find('div', {'class': 'field--name-field-total-amount'})
        total_amount = total_amount_element.text.strip() if total_amount_element else 'Unknown'

        table = soup.find('table')

        table_data = []

        if table:
            rows = table.find_all('tr')

            for row in rows[1:]:
                cells = row.find_all('td')

                # Skip summary or total rows
                if any(cell.has_attr('colspan') for cell in cells):
                    continue
                
                if len(cells) >= 8:
                    try:
                        allocation_code = clean_text(cells[0])
                        allocation = clean_text(cells[1])
                        emergency_type = clean_text(cells[2])
                        agency = clean_text(cells[3])
                        country = clean_text(cells[4])
                        project_code = clean_text(cells[5])
                        project_description = clean_text(cells[6])
                        window = clean_text(cells[7]).replace('Window:', '').strip()
                        sector = clean_text(cells[8]).replace('Sector:', '').strip()
                        approved_amount = clean_approved_amount(clean_text(cells[9]))
                        approval_date = clean_date_format(clean_text(cells[10]).replace('Approval date:', '').strip())
                        disbursement_date = clean_date_format(clean_text(cells[11]).replace('Disbursement date:', '').strip())

                        # Fetch additional project details dynamically
                        project_details = fetch_project_details(allocation_code, project_code, year_range.split("-")[0], link_id)

                        table_data.append({
                            'link_id': link_id,
                            'allocation_code': allocation_code,
                            'allocation': allocation,
                            'emergency_type': emergency_type,
                            'agency': agency,
                            'country': country,
                            'project_code': project_code,
                            'project_description': project_description,
                            'window': window,
                            'sector': sector,
                            'approved_amount': approved_amount,
                            'approval_date': approval_date,
                            'disbursement_date': disbursement_date,
                            'groups_targeted': project_details['groups_targeted'],
                            'number_of_people_targeted': project_details['number_of_people_targeted'],
                            'implementation_dates': project_details['implementation_dates']
                        })
                    except IndexError as e:
                        print(f"Error processing row: {cells} - {e}")
                        continue

        return table_data
    else:
        print(f"Error fetching data for link ID {link_id}: {response.status_code}")
        return []

def main():
    emergency_list = fetch_emergency_list()
    
    if not emergency_list:
        print("No emergency data found.")
        return

    all_table_data = []

    for emergency in emergency_list:
        link_id = emergency['link_id']
        name = emergency['name']
        print(f"Fetching data for link ID {link_id} ({name})...")
        table_data = fetch_emergency_details(link_id)
        all_table_data.extend(table_data)

    df = pd.DataFrame(all_table_data)
    output_csv = './data/cerf/cerf_emergency_data.csv'
    df.to_csv(output_csv, index=False)

    print(f"Data saved to {output_csv}")

if __name__ == "__main__":
    main()
