
# Event Pairing and Linking Logic

This document outlines the logic for pairing and linking disaster events across multiple datasets to build a unified global disaster database.

---

## **Matching Logic Across All Datasets**

| **Dataset/Column**                        | **Dataset/Column**                        | **Match Logic**                                                                 |
|-------------------------------------------|-------------------------------------------|---------------------------------------------------------------------------------|
| `event_ID` (event_Level_cleaned.csv)      | `event_ID` (hazard_Data_cleaned.csv, impact_Data_cleaned.csv) | **Blue**: Direct match for identical events.                                    |
| `ev_sdate` / `ev_fdate` (event_Level_cleaned.csv) | `haz_sdate` / `haz_fdate` (hazard_Data_cleaned.csv) | **Green**: Dates align within ±7 days for matching events.                      |
| `ev_sdate` / `ev_fdate` (event_Level_cleaned.csv) | `imp_sdate` / `imp_fdate` (impact_Data_cleaned.csv) | **Green**: Temporal alignment for events with associated impacts.               |
| `ev_sdate` / `ev_fdate` (event_Level_cleaned.csv) | `targ_evsdate` / `targ_evfdate` (ifrc-monty.xlsx)  | **Green**: Match source and destination events by date ranges in Monty Pairing Validation. |
| `ev_ISO3s` (event_Level_cleaned.csv)      | `haz_ISO3s` / `imp_ISO3s` (hazard_Data_cleaned.csv, impact_Data_cleaned.csv) | **Orange**: Events occur in the same country (ISO3 codes).                      |
| `ev_ISO3s` (event_Level_cleaned.csv)      | `targ_evISOs` / `dest_evISOs` (ifrc-monty.xlsx)    | **Orange**: ISO3 match between source and destination events.                   |
| `ev_name` (event_Level_cleaned.csv)       | `Disaster` (disaster-charter.csv)          | **Yellow**: Fuzzy match for event names (≥80% similarity).                      |
| `ev_name` (event_Level_cleaned.csv)       | `description` (ifrc-monty.xlsx)            | **Yellow**: Fuzzy match to Monty Pairing Validation descriptions.               |
| `gen_location` (event_Level_cleaned.csv)  | `haz_spat_fileloc` (hazard_Data_cleaned.csv) | **Pink**: Locations match directly or are within a defined spatial threshold (e.g., ≤50 km). |
| `gen_location` (event_Level_cleaned.csv)  | `targ_lon` / `targ_lat` (ifrc-monty.xlsx) | **Pink**: Geospatial proximity for related events.                              |
| `all_hazs_Ab` (event_Level_cleaned.csv)   | `all_hazs_Ab` (hazard_Data_cleaned.csv)    | **Orange**: Same hazard type across event and hazard datasets.                  |
| `all_hazs_Ab` (event_Level_cleaned.csv)   | `targ_hzAb` / `dest_hzAb` (ifrc-monty.xlsx) | **Orange**: Match hazard types between source and destination events.           |
| `imp_value` (impact_Data_cleaned.csv)     | `number_of_people_targeted` (cerf.csv)     | **Purple**: Similar impact metrics indicate related funding and population targeting. |
| `approved_amount` (cerf.csv)              | `imp_value` (impact_Data_cleaned.csv)      | **Purple**: Match financial data to associated impact data using the event ID or proximity logic. |
| `Year, Month, Date` (disaster-charter.csv)| `ev_sdate` / `haz_sdate` (event_Level_cleaned.csv, hazard_Data_cleaned.csv) | **Green**: Temporal match for disaster charter activation and event or hazard occurrence. |
| `Activation ID` (disaster-charter.csv)    | `allocation_code` (cerf.csv)               | **Red**: Link disaster charter activations to CERF funding allocations where applicable. |

---

## **Linking Logic for Related Events**

| **Primary Event Dataset/Column**         | **Related Event Dataset/Column**          | **Relationship Logic**                                                        |
|------------------------------------------|-------------------------------------------|--------------------------------------------------------------------------------|
| `event_ID` (Event Level)                 | `haz_sub_ID` / `haz_sdate` / `haz_fdate` (Hazard Data) | **Green**: Event linked to specific hazard occurrences by ID and date.        |
| `all_hazs_Ab` (Event Level)              | `all_hazs_Ab` (Hazard Data)               | **Orange**: Hazard type relationship: e.g., storms leading to floods.         |
| `approved_amount` (CERF)                 | `event_ID` (Event Level)                  | **Purple**: Funding linked to event by ID, dates, and ISO3.                   |
| `imp_value` (Impact Data)                | `number_of_people_targeted` (CERF)        | **Yellow**: Impact metrics inform funding targeting.                          |
| `targ_evID` (Monty Pairing)              | `dest_evID` (Monty Pairing)               | **Blue**: Match source and destination events using distance and date logic.  |

---

## **Color Coding for Manual Pairing Checks**

- **Blue**: Exact ID matches (`event_ID`, `targ_evID`, etc.).
- **Green**: Temporal matches (`ev_sdate`, `haz_sdate`, etc.).
- **Orange**: Geographic or country-based matches (`ev_ISO3s`, `haz_ISO3s`, etc.).
- **Yellow**: Fuzzy or descriptive matches (`ev_name`, `Disaster`).
- **Pink**: Spatial proximity (`gen_location`, `targ_lon`, `targ_lat`).
- **Purple**: Impact or financial metrics (`imp_value`, `approved_amount`).
- **Red**: Specific charter or funding activations (`Activation ID`, `allocation_code`).

---

## **Output Schema**

| **Field**               | **Description**                                                     |
|-------------------------|---------------------------------------------------------------------|
| `event_ID`              | Unified event identifier.                                          |
| `related_event_ID`      | For linked but distinct events.                                    |
| `ev_sdate`, `ev_fdate`  | Start and end dates for the event.                                 |
| `ev_ISO3s`              | ISO3 country code of the event.                                    |
| `all_hazs_Ab`           | Standardized hazard abbreviation.                                  |
| `imp_value`             | Consolidated impact metrics.                                       |
| `approved_amount`       | Consolidated funding data.                                         |
| `sources`               | List of datasets contributing to the record.                      |
| `relationship_type`     | Describes the relationship (e.g., "caused_by", "funded_by").       |

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

This **README.md** provides a comprehensive structure and color-coded guide for pairing and linking disaster events across datasets.
