import pandas as pd
import os
import pycountry
import shutil
from src.unified.countires_iso import COUNTRIES
country_csv_path = "./static_data/country_name_iso3_table.csv"
country_df = pd.read_csv(country_csv_path)
COUNTRY_MAPPING = country_df.set_index("country_name")["country_iso3"].to_dict()

dataframes = {
    "glide": pd.read_csv('./data_mid_1/glide/glide_mid1.csv').copy(),
    "gdacs": pd.read_csv('./data_mid_1/gdacs/gdacs_mid1.csv').copy(),
    "disaster_charter": pd.read_csv('./data_mid_1/disaster_charter/disaster_charter_mid1.csv').copy(),
    "emdat": pd.read_csv('./data_mid_1/emdat/emdat_mid1.csv').copy(),
    "idmc": pd.read_csv('./data_mid_1/idmc_idu/idus_mid1.csv').copy(),
    "cerf": pd.read_csv('./data_mid_1/cerf/cerf_mid1.csv').copy(),
    "ifrc": pd.read_csv('./data_mid_1/ifrc_eme/ifrc_eme_mid1.csv').copy()
}

# to read all the dataframes and find their column 'Country' if in this column are more than one values to split them into different rows and
# keep the same information even though are duplicated , so one event has Country : [country1, country2] and Date XXXXXXXX will be split into two rows
# one with Country: country1 and another with Country: country2 and Date XXXXXXXX and all the rest the same even if they are the same we keep them
def split_and_update_country_rows(df, country_col="Country", code_col="Country_Code", sep=","):
    """
    Splits rows in the DataFrame where the 'country_col' contains multiple country values.
    If a cell has multiple countries (as a string or list), the row is split into multiple rows,
    one per country, while preserving all the other column values. Also standardizes the 'Country_Code'
    to be a list with the ISO3 code in capital letters using the COUNTRIES constant if available,
    otherwise validates the country name using the pycountry library. If pycountry cannot find the country,
    an empty list is returned.
    
    Parameters:
      df (pd.DataFrame): Input DataFrame.
      country_col (str): Column name with country information.
      code_col (str): Column name with country code information.
      sep (str): Separator used to split country values in a string.
      
    Returns:
      pd.DataFrame: DataFrame with exploded country values and standardized country codes.
    """
    def ensure_list(cell):
        if isinstance(cell, (list, tuple)):
            return list(cell)
        if isinstance(cell, str):
            cell = cell.strip("[]")
            return [item.strip(" '\"") for item in cell.split(sep)]
        return [cell]
    if country_col not in df.columns:
        return df
    df[country_col] = df[country_col].apply(ensure_list)
    df_exploded = df.explode(country_col).reset_index(drop=True)
    def update_country_code(row):
        country_name = row[country_col]
        iso3 = COUNTRY_MAPPING.get(country_name, "")
        if not iso3:
            try:
                country = pycountry.countries.lookup(country_name)
                iso3 = country.alpha_3
            except LookupError:
                iso3 = ""
        return iso3
    if code_col in df_exploded.columns:
        df_exploded[code_col] = df_exploded.apply(update_country_code, axis=1)
    return df_exploded


# for source, df in dataframes.items():
#     normalized_df = split_and_update_country_rows(df, country_col="Country", code_col="Country_Code", sep=",")
#     output_base_dir = './data_prep/'
#     os.makedirs(output_base_dir, exist_ok=True)
#     output_file = os.path.join(output_base_dir, f"{source}_prep.csv")
#     normalized_df.to_csv(output_file, index=False)
#     print(f"Normalized data for '{source}' saved to: {output_file}")
#     # and then i want to delete the data_mid_1 folder
#     shutil.rmtree(f'./data_mid_1/{source}')
#     print(f"Deleted data for '{source}'")
output_base_dir = './data_prep/'
os.makedirs(output_base_dir, exist_ok=True)


for source, df in dataframes.items():
    normalized_df = split_and_update_country_rows(
        df, 
        country_col="Country", 
        code_col="Country_Code", 
        sep=","
    )
    output_file = os.path.join(output_base_dir, f"{source}_prep.csv")
    normalized_df.to_csv(output_file, index=False)
    print(f"Normalized data for '{source}' saved to: {output_file}")

# After the loop finishes, delete the entire data_mid_1 directory
data_mid_1_dir = './data_mid_1'
if os.path.exists(data_mid_1_dir):
    shutil.rmtree(data_mid_1_dir)
    print(f"Deleted folder: {data_mid_1_dir}")
else:
    print(f"Directory {data_mid_1_dir} does not exist.")