import pandas as pd

from src.data_consolidation.dictionary import (
    STANDARD_COLUMNS,
    GLIDE_MAPPING,
    GDACS_MAPPING,
    DISASTER_CHARTER_MAPPING,
    EMDAT_MAPPING,
    IDMC_MAPPING,
    CERF_MAPPING,
    IFRC_EME_MAPPING,
)

GLIDE_INPUT_CSV = "./data/glide/glide_data_combined_all.csv"

glide_df_raw = pd.read_csv(GLIDE_INPUT_CSV)

