import pandas as pd


def inspect_csv(file_paths):
    for file_path in file_paths:
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            print(f"Columns in {file_path}: {list(df.columns)}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

def main():
    file_paths = ["/home/evangelos/src/disaster-impact/data/event_Level_cleaned.csv", "/home/evangelos/src/disaster-impact/data/hazard_Data_cleaned.csv","/home/evangelos/src/disaster-impact/data/impact_Data_cleaned.csv", "/home/evangelos/Downloads/blob-disaster-impact/raw/human-validated/ifrc-monty/Copy of Monty Pairing Validation Data Sample.xlsx", "/home/evangelos/Downloads/blob-disaster-impact/raw/disaster-charter/charter_activations_web_scrape_2000_2024.csv", "/home/evangelos/Downloads/blob-disaster-impact/raw/cerf/cerf_emergency_data_dynamic_web_scrape.csv"]
    inspect_csv(file_paths)

if __name__ == "__main__":
    main()