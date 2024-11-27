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


