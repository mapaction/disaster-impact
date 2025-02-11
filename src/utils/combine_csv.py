import pandas as pd 
import os
import geopandas as gpd

def combine_csvs(input_dir, output_file):
    """
    Combine all CSV files in a directory into a single CSV file.
    Args:
        input_dir (str): The directory containing the CSV files to combine.
        output_file (str): The path to the output CSV file.
    Returns:
        None
    This function reads all CSV files in the specified directory, combines them into a single DataFrame,
    and writes the combined DataFrame to the specified output file.
    """
    all_data = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_dir, file_name)
            df = pd.read_csv(file_path)
            all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Combined CSV saved to {output_file}")

def convert_csv_to_geoparquet(csv_file, geoparquet_file):
    """
    Converts a CSV file with x and y coordinates to a GeoParquet file.

    Args:
        csv_file (str): Path to the input CSV file.
        geoparquet_file (str): Path to the output GeoParquet file.

    Returns:
        None

    Example:
        convert_csv_to_geoparquet('input.csv', 'output.parquet')
    """
    df = pd.read_csv(csv_file)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.x, df.y), crs="EPSG:4326"
    )
    gdf.to_parquet(geoparquet_file, index=False)
    print(f"GeoParquet saved to {geoparquet_file}")


if __name__ == "__main__":
    input_dir = "./data/adam_data"
    output_file = "./data/adam_data/combined_adam_data.csv"
    combine_csvs(input_dir, output_file)

    combined_csv_file = output_file
    geoparquet_file = "./data/adam_data/combined_adam_data.parquet"
    convert_csv_to_geoparquet(combined_csv_file, geoparquet_file)
    geoparquet_file_gdf = gpd.read_parquet(geoparquet_file)
    print(geoparquet_file_gdf.head())