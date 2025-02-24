
# Event Pairing and Linking Logic

<!-- markdownlint-disable MD013 -->

This document outlines the logic for pairing and linking disaster events
across multiple datasets to build a unified global disaster database.

---

## **Datasets and Column Descriptions**

1. **Event Level Data** (`event_Level_cleaned.csv`)
   - Key Columns: `event_ID`, `ev_name`, `ev_sdate`,
   `ev_fdate`, `gen_location`, `ev_ISO3s`, `all_hazs_Ab`

2. **Hazard Data** (`hazard_Data_cleaned.csv`)
   - Key Columns: `event_ID`, `haz_sub_ID`, `haz_sdate`,
   `haz_fdate`, `all_hazs_Ab`, `haz_ISO3s`

3. **Impact Data** (`impact_Data_cleaned.csv`)
   - Key Columns: `event_ID`, `imp_sub_ID`, `imp_value`,
   `imp_sdate`, `imp_fdate`, `imp_ISO3s`

4. **Monty Pairing Validation Data** (`ifrc-monty.xlsx`)
   - Key Columns: `targ_evID`, `targ_evsdate`, `targ_lon`,
   `targ_lat`, `dest_evID`, `dest_lon`, `dest_lat`, `dist_km`

5. **Disaster Charter Data** (`disaster-charter.csv`)
   - Key Columns: `Activation ID`, `Date of Activation`,
   `Disaster`

6. **CERF Financial Data** (`cerf.csv`)
   - Key Columns: `allocation_code`, `approved_amount`,
   `number_of_people_targeted`, `country`

---

## **Manual Pairing Process**

For each event:
1. Review `event_ID` (Blue) and align identical events.
2. Cross-check dates (Green) and hazard types (Orange) for temporal and hazard matching.
3. Compare names/descriptions (Yellow) for fuzzy matches.
4. Validate spatial proximity using locations (Pink) or calculated distances (Cyan).
5. Ensure financial and impact metrics align for linked funding (Purple).
6. Document pairing in a QA column for tracking.

---

This **README.md** provides a comprehensive structure
and color-coded guide for pairing and linking disaster events across datasets.
