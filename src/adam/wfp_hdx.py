from hdx.api.configuration import Configuration
from hdx.utilities.useragent import UserAgent
from hdx.data.dataset import Dataset
import os
import requests

UserAgent.set_global(
    "wfp_hdx_downloader",
    "1.0",
    "ediaaktos@mapaction.org.com"
)

Configuration.create(hdx_site="prod", hdx_read_only=True)

OUTPUT_DIR = "./data/hdx_csv_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_DATASETS = [
    "WFP Advanced Disaster Analysis and Mapping - Earthquake Data",
    "WFP Advanced Disaster Analysis and Mapping - Flood Data",
    "WFP Advanced Disaster Analysis and Mapping - Cyclone Data"
]

def download_csv(dataset_name):
    """
    Download all CSV resources for a given dataset.
    """
    dataset = Dataset.read_from_hdx(dataset_name)
    resources = dataset.get_resources()
    for resource in resources:
        if resource["format"].lower() == "csv":
            print(f"Downloading: {resource['name']} from {resource['url']}")
            response = resource.download(folder=OUTPUT_DIR)
            if response:
                print(f"Saved to {response}")
            else:
                print(f"Failed to download: {resource['name']}")

def main():
    # Loop through the target datasets and process them
    for title in TARGET_DATASETS:
        datasets = Dataset.search_in_hdx(title, rows=1000)
        if not datasets:
            print(f"No datasets found for: {title}")
            continue
        for dataset in datasets:
            print(f"Processing dataset: {dataset['name']}, Title: {dataset['title']}")
            download_csv(dataset['name'])

if __name__ == "__main__":
    main()
