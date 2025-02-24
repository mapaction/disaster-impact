"""Utility functions for processing CSV files."""

import os
from pathlib import Path

import geopandas as gpd
import pandas as pd


def combine_csvs(input_dir: str, output_file: str) -> None:
    """Combine all CSV files in a directory into a single CSV file.

    Args:
        input_dir (str): The directory containing the CSV files to combine.
        output_file (str): The path to the output CSV file.

    Returns:
        None
    This function reads all CSV files in the specified directory,
    combines them into a single DataFrame,
    and writes the combined DataFrame to the specified output file.
    """
    all_data = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            file_path = Path(input_dir) / file_name
            file_data_frame = pd.read_csv(file_path)
            all_data.append(file_data_frame)

    combined_data_frame = pd.concat(all_data, ignore_index=True)
    combined_data_frame.to_csv(output_file, index=False)


def convert_csv_to_geoparquet(csv_file: str, geoparquet_file: str) -> None:
    """Converts a CSV file with x and y coordinates to a GeoParquet file.

    Args:
        csv_file (str): Path to the input CSV file.
        geoparquet_file (str): Path to the output GeoParquet file.

    Returns:
        None

    Example:
        convert_csv_to_geoparquet('input.csv', 'output.parquet')
    """
    csv_data = pd.read_csv(csv_file)
    gdf = gpd.GeoDataFrame(
        csv_data,
        geometry=gpd.points_from_xy(csv_data.x, csv_data.y),
        crs="EPSG:4326",
    )
    gdf.to_parquet(geoparquet_file, index=False)


if __name__ == "__main__":
    input_dir = "./data/adam_data"
    output_file = "./data/adam_data/combined_adam_data.csv"
    combine_csvs(input_dir, output_file)

    combined_csv_file = output_file
    geoparquet_file = "./data/adam_data/combined_adam_data.parquet"
    convert_csv_to_geoparquet(combined_csv_file, geoparquet_file)
    geoparquet_file_gdf = gpd.read_parquet(geoparquet_file)
