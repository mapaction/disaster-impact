import os
from io import BytesIO
import json
import pandas as pd
from azure.storage.blob import BlobClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()

def load_env_vars():
    sas_token = os.getenv("STORAGE_SAS_TOKEN_")
    container_name = os.getenv("CONTAINER_NAME")
    storage_account = os.getenv("STORAGE_ACCOUNT")
    
    if not all([sas_token, container_name, storage_account]):
        raise EnvironmentError("One or more required environment variables are missing.")
    
    return sas_token, container_name, storage_account

def read_blob_to_dataframe(blob_name):
    sas_token, container_name, storage_account = load_env_vars()
    blob_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    blob_client = BlobClient.from_blob_url(blob_url)
    
    try:
        blob_data = blob_client.download_blob().content_as_bytes()
        if blob_name.endswith('.csv'):
            df = pd.read_csv(BytesIO(blob_data))
        elif blob_name.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(blob_data))
        else:
            raise ValueError("Unsupported file format. Only .csv and .xlsx are supported.")
        return df
    except Exception as e:
        print(f"Error reading blob: {e}")
        raise

def read_blob_to_json(blob_name):
    sas_token, container_name, storage_account = load_env_vars()
    blob_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    blob_client = BlobClient.from_blob_url(blob_url)
    
    try:
        blob_data = blob_client.download_blob().content_as_bytes()
        data = json.loads(blob_data.decode("utf-8"))  # Decode bytes to JSON
        return data
    except Exception as e:
        print(f"Error reading JSON blob: {e}")
        raise

def combine_csvs_from_blob_dir(blob_dir: str) -> pd.DataFrame:
    sas_token, container_name, storage_account = load_env_vars()
    container_url = f"https://{storage_account}.blob.core.windows.net/{container_name}?{sas_token}"
    container_client = ContainerClient.from_container_url(container_url)
    
    combined_df = pd.DataFrame()

    blob_list = container_client.list_blobs(name_starts_with=blob_dir)

    for blob in blob_list:
        if blob.name.endswith(".csv"):
            print(f"Reading blob: {blob.name}")
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().content_as_bytes()
            temp_df = pd.read_csv(BytesIO(blob_data))
            combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

    return combined_df