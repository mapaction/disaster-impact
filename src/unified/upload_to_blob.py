from src.utils.azure_blob_utils import upload_dir_to_blob

if __name__ == "__main__":
    upload_dir_to_blob("data_mid", "mid")
    upload_dir_to_blob("data_out", "out")
