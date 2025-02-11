import os
from io import BytesIO
import json
import pandas as pd
from azure.storage.blob import BlobClient, ContainerClient , BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

def load_env_vars():
    """
    Load environment variables for Azure Blob Storage.
    This function retrieves the SAS token, container name, and storage account
    from the environment variables. If any of these variables are missing, it
    raises an EnvironmentError.
    Returns:
        tuple: A tuple containing the SAS token, container name, and storage account.
    Raises:
        EnvironmentError: If one or more required environment variables are missing.
    """
    sas_token = os.getenv("STORAGE_SAS_TOKEN_")
    container_name = os.getenv("CONTAINER_NAME")
    storage_account = os.getenv("STORAGE_ACCOUNT")
    
    if not all([sas_token, container_name, storage_account]):
        raise EnvironmentError("One or more required environment variables are missing.")
    
    return sas_token, container_name, storage_account

def read_blob_to_dataframe(blob_name, **read_csv_kwargs):
    """
    Reads a blob (file) from Azure Blob Storage and loads it into a pandas DataFrame.
    Parameters:
    blob_name (str): The name of the blob (file) to read.
    **read_csv_kwargs: Additional keyword arguments to pass to pandas.read_csv().
    Returns:
    pd.DataFrame: The data from the blob loaded into a pandas DataFrame.
    Raises:
    ValueError: If the file format is not supported (only .csv and .xlsx are supported).
    Exception: If there is an error reading the blob.
    Example:
    df = read_blob_to_dataframe('data.csv', delimiter=',')
    """
    sas_token, container_name, storage_account = load_env_vars()
    blob_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    blob_client = BlobClient.from_blob_url(blob_url)
    
    try:
        blob_data = blob_client.download_blob().content_as_bytes()
        if blob_name.endswith('.csv'):
            df = pd.read_csv(BytesIO(blob_data), **read_csv_kwargs)
        elif blob_name.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(blob_data))
        else:
            raise ValueError("Unsupported file format. Only .csv and .xlsx are supported.")
        return df
    except Exception as e:
        print(f"Error reading blob: {e}")
        raise

def read_blob_to_json(blob_name):
    """
    Reads a JSON blob from Azure Blob Storage and returns it as a dictionary.
    Args:
        blob_name (str): The name of the blob to read.
    Returns:
        dict: The JSON data from the blob.
    Raises:
        Exception: If there is an error reading the blob.
    """
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
    """
    Combine all CSV files from a specified Azure Blob Storage directory into a single DataFrame.
    Args:
        blob_dir (str): The directory path in the Azure Blob Storage container.
    Returns:
        pd.DataFrame: A DataFrame containing the combined data from all CSV files in the specified directory.
    """
    sas_token, container_name, storage_account = load_env_vars()
    container_url = f"https://{storage_account}.blob.core.windows.net/{container_name}?{sas_token}"
    container_client = ContainerClient.from_container_url(container_url)
    
    combined_df = pd.DataFrame()

    blob_list = container_client.list_blobs(name_starts_with=blob_dir)

    for blob in blob_list:
        if blob.name.endswith(".csv"):
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().content_as_bytes()
            temp_df = pd.read_csv(BytesIO(blob_data))
            combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

    return combined_df

def upload_dir_to_blob(local_dir, blob_dir):
    """
    Uploads all files from a local directory to an Azure Blob Storage container.

    Args:
        local_dir (str): The path to the local directory containing files to upload.
        blob_dir (str): The directory path within the blob container where files will be uploaded.

    Raises:
        ValueError: If the specified local directory does not exist.
        Exception: If there is an error during the upload process.

    Example:
        upload_dir_to_blob("/path/to/local/dir", "target/blob/dir")
    """

    sas_token, container_name, storage_account = load_env_vars()
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account}.blob.core.windows.net", credential=sas_token)
    container_client = blob_service_client.get_container_client(container_name)

    if not os.path.isdir(local_dir):
        raise ValueError(f"The directory {local_dir} does not exist.")

    for root, _, files in os.walk(local_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, local_dir).replace("\\", "/")
            blob_path = f"disaster-impact/{blob_dir}/{relative_path}"

            try:
                with open(file_path, "rb") as data:
                    blob_client = container_client.get_blob_client(blob_path)
                    blob_client.upload_blob(data, overwrite=True, timeout=600)
                    print(f"Uploaded {file_path} to {blob_path}")
            except Exception as e:
                print(f"Error uploading {file_path}: {e}")
                raise
