import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Define base URL and dynamically add the current date
def get_dynamic_disaster_api_url():
    base_url = 'https://disasterscharter.org/en/web/guest/charter-activations'
    today = datetime.today().strftime('%d+%m+%Y')
    query_params = f'?from=01+01+2000&to={today}&p_p_id=charterActivationsFiltered_WAR_charterportlets&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getActivations&p_p_col_id=column-1&p_p_col_count=1&disaster=&region='
    return f"{base_url}{query_params}"

output_dir = './data/cgt'
os.makedirs(output_dir, exist_ok=True)

def fetch_activation_details(link):
    base_url = 'https://disasterscharter.org'
    url = f"{base_url}{link}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {
            'type_of_event': soup.find(string="Type of Event:").find_next().text.strip() if soup.find(string="Type of Event:") else 'N/A',
            'location_of_event': soup.find(string="Location of Event:").find_next().text.strip() if soup.find(string="Location of Event:") else 'N/A',
            'date_of_activation': soup.find(string="Date of Charter Activation:").find_next().text.strip() if soup.find(string="Date of Charter Activation:") else 'N/A',
            'time_of_activation': soup.find(string="Time of Charter Activation:").find_next().text.strip() if soup.find(string="Time of Charter Activation:") else 'N/A',
            'timezone': soup.find(string="Time zone of Charter Activation:").find_next().text.strip() if soup.find(string="Time zone of Charter Activation:") else 'N/A',
            'charter_requestor': soup.find(string="Charter Requestor:").find_next().text.strip() if soup.find(string="Charter Requestor:") else 'N/A',
            'activation_id': soup.find(string="Activation ID:").find_next().text.strip() if soup.find(string="Activation ID:") else 'N/A',
            'project_management': soup.find(string="Project Management:").find_next().text.strip() if soup.find(string="Project Management:") else 'N/A',
            'value_adding': soup.find(string="Value Adding:").find_next().text.strip() if soup.find(string="Value Adding:") else 'N/A',
        }
        
        return details
    else:
        print(f"Failed to fetch activation details from {url}")
        return {}

def fetch_disaster_activations():
    disaster_api_url = get_dynamic_disaster_api_url()  # Fetch the dynamic URL with today's date
    response = requests.get(disaster_api_url)

    if response.status_code == 200:
        try:
            data = response.json()
            print("Data received:", data)  # Debug print to inspect raw data
            save_activations_to_csv(data)
        except ValueError:
            print("Response is not in JSON format")
            print(response.text)  # Debug print to see the raw response
    else:
        print(f"Error fetching disaster charter activations: {response.status_code}")

def save_activations_to_csv(data):
    csv_file_path = os.path.join(output_dir, 'disaster_activations_boosted_oct.csv')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['Year', 'Month', 'Date', 'Disaster', 'Formatted Date', 'Details Link', 'Type of Event', 'Location of Event', 'Date of Activation', 'Time of Activation', 'Timezone', 'Charter Requestor', 'Activation ID', 'Project Management', 'Value Adding'])

        for year_data in data:
            year = year_data['year']
            activations_by_month = year_data['activationsMonth']

            for month, activations in activations_by_month.items():
                for activation in activations:
                    title = activation['title']
                    formatted_date = activation['formatedDate']
                    link = activation['link']
                    full_link = f"https://disasterscharter.org{link}"
                    activation_timestamp = activation['activationDate']
                    activation_date = datetime.utcfromtimestamp(activation_timestamp / 1000).strftime('%Y-%m-%d')

                    details = fetch_activation_details(link)

                    writer.writerow([
                        year, month, activation_date, title, formatted_date, full_link,
                        details.get('type_of_event', 'N/A'),
                        details.get('location_of_event', 'N/A'),
                        details.get('date_of_activation', 'N/A'),
                        details.get('time_of_activation', 'N/A'),
                        details.get('timezone', 'N/A'),
                        details.get('charter_requestor', 'N/A'),
                        details.get('activation_id', 'N/A'),
                        details.get('project_management', 'N/A'),
                        details.get('value_adding', 'N/A')
                    ])

    print(f"Data saved to {csv_file_path}")

def main():
    fetch_disaster_activations()

if __name__ == "__main__":
    main()
