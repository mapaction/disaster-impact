
# Disaster Impact Data Processing

This project is designed to process and analyze data from the Monty API, a global crisis data bank. It includes scripts for downloading and flattening deeply nested JSON data into structured CSV files for easier analysis. The project supports multiple data sections, including `monty_Info`, `event_Level`, `impact_Data`, `hazard_Data`, `response_Data`, and `taxonomies`.

---

## Project Structure

```
.
├── LICENSE                        # License for the project
├── Makefile                       # Makefile for automating common tasks
├── notebooks                      # Jupyter notebooks for exploration and analysis
│   ├── data_inspector.ipynb       # Notebook for inspecting data
│   ├── __init__.py                # Notebook package initialisation
│   ├── new_sandbox.ipynb          # New sandbox notebook
│   └── process_sandbox.ipynb      # Notebook for processing sandbox data
├── poetry.lock                    # Poetry lock file for dependency management
├── poetry.toml                    # Poetry configuration
├── pyproject.toml                 # Project metadata and dependencies
├── README.md                      # Project documentation
├── docs                           # Documentation files
│   ├── PAIRING.md                 # Documentation on pairing logic
│   └── TABLES.md                  # Documentation on data tables
├── src                            # Source code
│   ├── adam                       # Module for handling ADAM data
│   │   ├── __init__.py            # ADAM module initialisation
│   │   ├── wfp_adam_downloader.py # ADAM data downloader
│   ├── cerf                       # Module for handling CERF data
│   │   ├── __init__.py            # CERF module initialisation
│   │   ├── cerf_downloader.py     # CERF data downloader
│   │   ├── data_normalisation_cerf.py # CERF data normalisation script
│   │   ├── cerf_schema.json       # CERF JSON schema
│   ├── data_consolidation         # Data consolidation scripts
│   │   ├── __init__.py            # Data consolidation module initialisation
│   │   ├── data_consolidation.py  # Main data consolidation script
│   │   ├── dictionary.py          # Dictionary utilities for consolidation
│   ├── disaster_charter           # Module for handling Disaster Charter data
│   │   ├── __init__.py            # Disaster Charter module initialisation
│   │   ├── data_downloader_dc.py  # Disaster Charter data downloader
│   │   ├── data_normalisation_dc.py # Disaster Charter data normalisation
│   │   ├── disaster_charter_schema.json # Disaster Charter JSON schema
│   ├── emdat                      # Module for handling EMDAT data
│   │   ├── data_normalisation_emdat.py # EMDAT data normalisation script
│   │   ├── emdat_schema.json      # EMDAT JSON schema
│   ├── gdacs                      # Module for handling GDACS data
│   │   ├── __init__.py            # GDACS module initialisation
│   │   ├── combine_csv_gdacs.py   # GDACS CSV combination script
│   │   ├── data_downloader_gdacs.py # GDACS data downloader
│   │   ├── data_normalisation_gdacs.py # GDACS data normalisation
│   │   ├── gdacs_schema.json      # GDACS JSON schema
│   ├── glide                      # Module for handling GLIDE data
│   │   ├── __init__.py            # GLIDE module initialisation
│   │   ├── data_download_glide.py # GLIDE data downloader
│   │   ├── data_normalisation_glide.py # GLIDE data normalisation
│   │   ├── glide_schema.json      # GLIDE JSON schema
│   ├── idmc                       # Module for handling IDMC data
│   │   ├── data_normalisation_idmc.py # IDMC data normalisation script
│   │   ├── idmc_schema.json       # IDMC JSON schema
│   ├── ifrc_eme                   # Module for handling IFRC EME data
│   │   ├── data_normalisation_ifrc_eme.py # IFRC EME data normalisation script
│   │   ├── ifrc_eme_schema.json   # IFRC EME JSON schema
│   ├── unified                    # Unified data processing
│   │   ├── __init__.py            # Unified module initialisation
│   │   ├── charts                 # Charts and diagrams
│   │   │   ├── data_flow.drawio   # Data flow chart
│   │   │   └── flow_chart_final.drawio # Final flowchart
│   │   ├── countires_iso.py       # Country ISO codes utility
│   │   ├── dictionaries           # Dictionary utilities
│   │   │   └── dictionary_events.py # Dictionary for event mapping
│   │   ├── pipeline.py            # Unified data pipeline script
│   │   ├── unified_json_schema    # Unified JSON schema
│   │   │   └── unified_schema.json # Unified data schema
│   │   └── upload_to_blob.py      # Script to upload data to Azure Blob
│   └── utils                      # Utilities
│       ├── azure_blob_utils.py    # Azure Blob utility functions
│       ├── combine_csv.py         # CSV combination script
├── tests                          # Unit tests
│   ├── __init__.py                # Tests initialisation
│   ├── example                    # Example tests
│   │   ├── __init__.py            # Example tests initialisation
│   │   ├── test.drawio            # Test diagram
│   │   └── test_example.py        # Example test cases
```

---

## Features

- **Monty API Integration**:
  - Fetches data from the Monty API using an API token stored in environment variables.
  - Processes multiple sections of the API (e.g., `event_Level`, `impact_Data`).

- **Flattening JSON**:
  - Converts deeply nested JSON into a tabular format (CSV).
  - Extracts only the last key in nested structures for simpler column naming.

- **CSV Output**:
  - Each section is saved as a separate CSV file in the `data` directory.

- **Automation**:
  - Includes a `Makefile` for automating common tasks like dependency installation, testing, and linting.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ediakatos/disaster-impact.git
   cd disaster-impact
   ```

2. Install dependencies using Poetry:
   ```bash
   make .venv
   ```

3. Set up the `.env` file with your Monty API token:
   ```plaintext
   MONTY_API_TOKEN=<your_api_token>
   ```

---

## Usage

### Fetch and Process Data
Run the script to fetch and process data from the Monty API:
```bash
make run
```

This will:
- Fetch data from the Monty API.
- Flatten nested JSON structures.
- Save each section as a CSV file in the `data` directory.

### Example CSV Output
A processed `event_Level` CSV will look like this:
| event_ID                                  | ev_name | ext_ID        | ext_ID_db   | ext_ID_org | ev_sdate   | ev_fdate   | gen_location                 | ev_ISO3s | all_hazs_Ab | all_hazs_spec |
|-------------------------------------------|---------|---------------|-------------|------------|------------|------------|------------------------------|----------|-------------|---------------|
| monty_031f0987-9d17-4007-9665-85b85448af82 | sequia  | ARG-7838-a    | Desinventar | UNDRR      | 2007-08-20 | 2067-08-05 | Cuenca Desaguadero-Salado    | ARG      | DR          | MH0035        |

---

## Testing

Run unit tests with:
```bash
make test
```

---

## Linting

Check code quality and formatting with:
```bash
make lint
```

---

## Clean Environment

Remove the virtual environment and dependencies:
```bash
make clean
```

---

## Development Notes

### Key Script: `process_monty_data.py`
This script handles:
- Fetching data from the Monty API.
- Flattening nested JSON structures into tabular format.
- Saving processed data to CSV files.

### Makefile Commands
- `make help`: Displays available commands.
- `make .venv`: Installs project dependencies.
- `make hooks`: Adds pre-commit hooks.
- `make test`: Runs unit tests.
- `make lint`: Runs lint tests.
- `make clean`: Removes the virtual environment.
- `make run`: Runs the Monty API data processing script.

---

## License

This project is licensed under the terms specified in the `LICENSE` file.

---

## Contributions

Contributions, issues, and feature requests are welcome. Please feel free to submit a pull request or open an issue on the repository.

---

## Author

Evangelos Diakatos
