import pandas as pd
import os

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
def split_country_rows(df, country_col="Country", sep=","):
    """
    Splits rows in the DataFrame where the 'country_col' contains multiple country values.
    If a cell has multiple countries (as a string or list), the row is split into multiple rows,
    one per country, while preserving all the other column values.
    
    Parameters:
      df (pd.DataFrame): Input DataFrame.
      country_col (str): Column name with country information.
      sep (str): Separator used to split country values in a string.
      
    Returns:
      pd.DataFrame: DataFrame with exploded country values.
    """
    def ensure_list(cell):
        if isinstance(cell, (list, tuple)):
            return list(cell)
        if isinstance(cell, str):
            cell = cell.strip("[]")
            countries = [item.strip(" '\"") for item in cell.split(sep)]
            return countries
        return [cell]

    if country_col not in df.columns:
        return df


    df[country_col] = df[country_col].apply(ensure_list)
    df_exploded = df.explode(country_col).reset_index(drop=True)
    return df_exploded

output_base_dir = './data_mid_2/'
os.makedirs(output_base_dir, exist_ok=True)

for source, df in dataframes.items():
    normalized_df = split_country_rows(df, country_col="Country", sep=",")
    source_output_dir = os.path.join(output_base_dir, source)
    os.makedirs(source_output_dir, exist_ok=True)
    output_file = os.path.join(source_output_dir, f"{source}_mid2.csv")
    normalized_df.to_csv(output_file, index=False)
    print(f"Normalized data for '{source}' saved to: {output_file}")
