# Disaster Impact Database

**Disaster Impact Database** is an open-source project designed to ingest,
process, and analyse disaster-related data from multiple sources.
The project reads raw data from Azure Blob Storage, normalises CSV files,
and lays the groundwork for future data consolidation and analysis.
Data sources include **GLIDE**, **GDACS**, **CERF**, **EMDAT**,
**IDMC**, **IFRC** and more.

## Project Purpose

The primary goal is to build a unified disaster impact database that:

- **Downloads raw data** from Azure Blob Storage.
- **Curates and normalises** data from various humanitarian and disaster sources.
- **Standardixes** data into consistent formats using JSON schemas.
- **Exports data** as normalised CSV files.
- **Prepares for future consolidation** by grouping events by type, country,
and event date (with a ±7 days window).

## Project Structure

```bash
.
├── docs                # Documentation
├── LICENSE             # Project license
├── Makefile            # Automation commands
├── notebooks           # Jupyter notebooks for data inspection and experimentation
├── poetry.lock         # Poetry lock file for dependencies
├── poetry.toml         # Poetry configuration
├── pyproject.toml      # Project metadata and dependency management
├── README.md           # This file
├── src                 # Source code modules
│   ├── cerf          # CERF data processing (downloader, normalization, schema)
│   ├── data_consolidation  # Future module for data consolidation tasks
│   ├── disaster_charter    # Disaster Charter data processing
│   ├── emdat         # EM-DAT data processing
│   ├── gdacs         # GDACS data processing
│   ├── glide         # GLIDE data processing
│   ├── idmc          # IDMC data processing
│   ├── ifrc_eme      # IFRC data processing
│   ├── unified       # Unified schema, consolidated data, and blob upload utilities
│   └── utils         # Utility scripts
├── static_data         # Static reference data (e.g., country codes, event codes)
└── tests               # Unit and integration tests
```

## Key Features

- **Data Download**: Retrieve raw data directly from Azure Blob Storage.
- **Data Curation**: Clean and preprocess raw data.
- **Normalisation & Standardisation**: Process and flatten,
ensuring data from different sources is standardised.
- **Data Schemas**: Use JSON schemas to validate and enforce data structure consistency.
- **CSV Output**: Export normalized data
to CSV for downstream analysis.
- **Future Data Consolidation**: Group events by type, country, and event date
(with a ±7 days window) to create a consolidated dataset.
- **Automation**: Utilise Makefile commands for environment setup,
testing, linting, and more.

## Usage Instructions

### Environment Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management.
To set up your development environment:

1. **Create and activate the virtual environment:**

   ```bash
   make .venv
   ```

2. **Install project dependencies:**

   ```bash
   poetry install
   ```

### Running Normalisation Scripts

Each data source module under `src` contains scripts for data normalisation.
For example, to run the normalisation process for GLIDE data:

```bash
python -m src.glide.data_normalisation_glide
```

Replace `glide` with the appropriate module name for other data sources
(e.g., `gdacs`, `cerf`, etc.).

### Automation with Makefile

The included `Makefile` provides several automation commands:

- **Set up the environment:**

  ```bash
  make .venv
  ```

- **Run tests:**

  ```bash
  make test
  ```

- **Lint the code:**

  ```bash
  make lint
  ```

- **Clean the environment:**

  ```bash
  make clean
  ```

## Testing, Linting, and Environment Cleanup

- **Testing**: Run unit and integration tests located in the `tests` directory.

  ```bash
  make test
  ```

- **Linting**: Check code quality with linting tools.

  ```bash
  make lint
  ```

- **Clean Environment**: Remove temporary files and reset the environment as needed.

  ```bash
  make clean
  ```

## Development Notes & Key Scripts

- **Key Scripts:**
  - **Normalization:** `src/*/data_normalisation*.py`
  - **JSON Schemas:** Located in each module (e.g., `src/cerf/cerf_schema.json`)
  - **CSV Processing:** `src/utils/combine_csv.py`, `src/utils/splitter.py`
  - **Future Consolidation:** `src/data_consolidation/`

- **Development Notes:**
  - Update JSON schemas as the data structure evolves.
  - Extend the Makefile for additional automation tasks.
  - Contributions to enhance data consolidation features are highly encouraged.

## Contributing

Contributions are welcome! To contribute:
- Clone the repository and create a branch from `main`.
- Submit pull requests with detailed descriptions of your changes.

## License

This project is licensed under the GNU GENERAL PUBLIC license.
See the [LICENSE](./LICENSE) file for details.

## Author Information

- **Author:** ediakatos
- **Contact:** ediakatos@mapaction.org

---

Thank you for using the Disaster Impact Database!
For issues or feature requests, please open an issue on GitHub. Happy coding!
