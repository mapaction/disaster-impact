
# Event Pairing and Linking Logic

This document outlines the logic for pairing and linking disaster events across multiple datasets to build a unified global disaster database.

---

## **Datasets and Column Descriptions**

1. **Event Level Data** (`event_Level_cleaned.csv`)
   - Key Columns: `event_ID`, `ev_name`, `ev_sdate`, `ev_fdate`, `gen_location`, `ev_ISO3s`, `all_hazs_Ab`

2. **Hazard Data** (`hazard_Data_cleaned.csv`)
   - Key Columns: `event_ID`, `haz_sub_ID`, `haz_sdate`, `haz_fdate`, `all_hazs_Ab`, `haz_ISO3s`

3. **Impact Data** (`impact_Data_cleaned.csv`)
   - Key Columns: `event_ID`, `imp_sub_ID`, `imp_value`, `imp_sdate`, `imp_fdate`, `imp_ISO3s`

4. **Monty Pairing Validation Data** (`ifrc-monty.xlsx`)
   - Key Columns: `targ_evID`, `targ_evsdate`, `targ_lon`, `targ_lat`, `dest_evID`, `dest_lon`, `dest_lat`, `dist_km`

5. **Disaster Charter Data** (`disaster-charter.csv`)
   - Key Columns: `Activation ID`, `Date of Activation`, `Disaster`

6. **CERF Financial Data** (`cerf.csv`)
   - Key Columns: `allocation_code`, `approved_amount`, `number_of_people_targeted`, `country`

---

## **Matching Logic**

| **Dataset/Column**                        | **Dataset/Column**                        | **Match Logic**                                                                 |
|-------------------------------------------|-------------------------------------------|---------------------------------------------------------------------------------|
| `event_ID` (Event Level)                  | `event_ID` (Hazard/Impact)                | **Blue**: Direct match for identical events.                                    |
| `ev_sdate` / `ev_fdate` (Event Level)     | `haz_sdate` / `haz_fdate` (Hazard Data)   | **Green**: Temporal alignment within ±7 days.                                   |
| `ev_ISO3s` (Event Level)                  | `haz_ISO3s` / `imp_ISO3s` (Hazard/Impact) | **Orange**: ISO3 codes match for same country.                                  |
| `ev_name` (Event Level)                   | `Disaster` (Disaster Charter)             | **Yellow**: Fuzzy match for names (≥80% similarity).                            |
| `gen_location` (Event Level)              | `haz_spat_fileloc` (Hazard Data)          | **Pink**: Spatial proximity within ≤50 km.                                      |
| `imp_value` (Impact Data)                 | `number_of_people_targeted` (CERF)        | **Purple**: Similar metrics confirm funding relationship.                       |
| `Activation ID` (Disaster Charter)        | `allocation_code` (CERF)                  | **Red**: Links charter activations to CERF funding allocations.                 |
| `targ_lon` / `targ_lat` (Monty Pairing)   | `dest_lon` / `dest_lat` (Monty Pairing)   | **Cyan**: Geospatial distance confirms related events (e.g., ≤50 km).           |

---

## **Linking Logic for Related Events**

| **Primary Event Dataset/Column**         | **Related Event Dataset/Column**          | **Relationship Logic**                                                        |
|------------------------------------------|-------------------------------------------|--------------------------------------------------------------------------------|
| `event_ID` (Event Level)                 | `haz_sub_ID` (Hazard Data)                | **Green**: Event linked to specific hazard occurrences by ID and date.        |
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
- **Cyan**: Geospatial matches with calculated distances (`dist_km`).

---

## **Output Schema**

| **Field**               | **Description**                                                     |
|-------------------------|---------------------------------------------------------------------|
| `event_ID`              | Unified event identifier.                                          |
| `related_event_ID`      | Links to related events.                                           |
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
