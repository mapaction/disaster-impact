import pandas as pd 
import os
import geopandas as gpd

def combine_csvs(input_dir, output_file):
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
        df = pd.read_csv(csv_file)
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.x, df.y), crs="EPSG:4326"
        )
        gdf.to_parquet(geoparquet_file, index=False)
        print(f"GeoParquet saved to {geoparquet_file}")

    combined_csv_file = output_file
    geoparquet_file = "./data/adam_data/combined_adam_data.parquet"
    convert_csv_to_geoparquet(combined_csv_file, geoparquet_file)

input_dir = "./data/adam_data"
output_file = "./data/adam_data/combined_adam_data.csv"
combine_csvs(input_dir, output_file)