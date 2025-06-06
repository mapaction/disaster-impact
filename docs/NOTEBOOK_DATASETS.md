# Notebook Data Sources

This document outlines the datasets consumed by the analysis notebooks. All datasets were downloaded in June 2025 and represent the latest available versions.

## Dataset Sources

- **GDACS** (API):
  - Description: Global Disaster Alert and Coordination System events.
  - Download Method: API
  - Location: `data/gdacs/`
  - Files: `gdacs_events_*.csv`

- **IDMC IDUS** (API):
  - Description: Internal Displacement Monitoring Centre IDUS dump.
  - Download Method: API
  - Location: `data/idmc_idu/`
  - File: `idus_all.json`

- **CERF** (Web Scrape):
  - Description: CERF emergency data.
  - Download Method: Web scrape
  - Location: `data/cerf/`
  - File: `cerf_emergency_data_dynamic_web_scrape.csv`

- **Disaster Charter** (Web Scrape):
  - Description: Charter activations.
  - Download Method: Web scrape
  - Location: `data/disaster-charter/`
  - File: `charter_activations_web_scrape_2000_2025.csv`

- **GLIDE** (Web Scrape):
  - Description: GLIDE events.
  - Download Method: Web scrape
  - Location: `data/glide/`
  - File: `glide_events.csv`

- **EMDAT** (Manual Download):
  - Description: EM-DAT custom request.
  - Download Method: Manual download
  - Location: `data/emdat/`
  - File: `public_emdat_custom_request_2025-06-04_c1e3334f-e027-4f8a-92d5-7ce401c7654c.xlsx`

- **IFRC EME** (Manual Download):
  - Description: IFRC emergencies.
  - Download Method: Manual download
  - Location: `data/ifrc_dref/`
  - File: `IFRC_emergencies.csv`

## Usage in Notebooks

The notebooks (`exploration.ipynb`, `process_sandbox.ipynb`) read these files directly from the `data/` directory to perform exploratory analysis and data processing.

## Notebook Analysis Logic

The `process_sandbox.ipynb` notebook performs the following steps:

- **Data Preprocessing**: Loads each dataset, renames and cleans columns, standardizes event dates, and maps event types to a common taxonomy.
- **Event Matching**: Combines all sources into a single `disaster_df` by merging events based on date proximity, event type, and country, creating boolean flags for each source.
- **Summary Table ("Number of events per source")**: Shows the total number of events originally in each dataset and the number of unique valid events after preprocessing.
- **Matching Events Table**: Compares, for each source, how many events are exclusive (only appear in that source) versus matched across multiple sources, and displays match percentages.
- **Overlap Matrix & Chord Diagram**: Constructs a matrix counting the number of shared events for every pair of sources and visualizes these overlaps as a circular chord diagram using `pycirclize`.
