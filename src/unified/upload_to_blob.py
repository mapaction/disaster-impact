"""Script for uploading 'data_mid' to their corresponding Azure Blob."""

from src.utils.azure_blob_utils import upload_dir_to_blob

if __name__ == "__main__":
    upload_dir_to_blob("data_prep", "prep")
    upload_dir_to_blob("data_out", "out")
