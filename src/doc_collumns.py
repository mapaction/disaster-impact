import pandas as pd


def get_columns(file_path):
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        return list(df.columns)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def main():

    csv = input("Enter the path to the csv file: ")
    columns = get_columns(csv)
    if columns:
        print(f"Columns in {csv}: {columns}")
    else:
        print("Could not read the file")

if __name__ == "__main__":
    main()