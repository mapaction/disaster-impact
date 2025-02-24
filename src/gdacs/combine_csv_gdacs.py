"""Combine all the csv files in the input directory into a single csv file."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from utils.combine_csv import combine_csvs

input_dir = "/home/evangelos/src/disaster-impact/data/gdacs_all_types_yearly_v3_fast"
output_file = (
    "/home/evangelos/src/disaster-impact"
    "/data/gdacs_all_types_yearly_v3_fast/combined_gdacs_data.csv"
)
combine_csvs(input_dir, output_file)
