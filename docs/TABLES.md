
# Event Pairing and Linking Logic

This document outlines the logic for pairing and linking disaster events across
multiple datasets to build a unified global disaster database.

---

---

## **Output Schema**

| **Field**               | **Description**  
|-------------------------|---------------------------
| `event_ID`              | Unified event identifier.
| `related_event_ID`      | For linked but distinct events.
| `ev_sdate`, `ev_fdate`  | Start and end dates for the event.
| `ev_ISO3s`              | ISO3 country code of the event.
| `all_hazs_Ab`           | Standardized hazard abbreviation.
| `imp_value`             | Consolidated impact metrics.
| `approved_amount`       | Consolidated funding data.
| `sources`               | List of datasets contributing to the record.
| `relationship_type`     | Describes the relationship (e.g., "caused_by", "funded_by").

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

This **README.md** provides a comprehensive structure and color-coded guide
for pairing and linking disaster events across datasets.
