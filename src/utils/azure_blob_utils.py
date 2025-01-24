import os
from io import BytesIO

import pandas as pd
from azure.storage.blob import BlobClient
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
        
        df = pd.read_csv(BytesIO(blob_data))
        return df
    except Exception as e:
        print(f"Error reading blob: {e}")
        raise