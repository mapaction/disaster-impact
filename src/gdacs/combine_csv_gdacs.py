import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adam.combine_csv import combine_csvs

input_dir = "/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v3_fast"
output_file = "/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v3_fast/combined_gdacs_data.csv"
combine_csvs(input_dir, output_file)
