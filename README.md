
# Disaster Impact Data Processing

This project is designed to process and analyze data from the Monty API, a global crisis data bank. It includes scripts for downloading and flattening deeply nested JSON data into structured CSV files for easier analysis. The project supports multiple data sections, including `monty_Info`, `event_Level`, `impact_Data`, `hazard_Data`, `response_Data`, and `taxonomies`.

---

## Project Structure

```
.
├── LICENSE                        # License for the project
├── Makefile                       # Makefile for automating common tasks
├── poetry.lock                    # Poetry lock file for dependency management
├── poetry.toml                    # Poetry configuration
├── pyproject.toml                 # Project metadata and dependencies
├── README.md                      # Project documentation
├── src                            # Source code
│   ├── __init__.py                # Package initialization
│   └── monty_flatten_scripts_download
│       ├── __inti__.py            # Subpackage initialization
│       └── process_monty_data.py  # Script to fetch and process Monty API data
└── tests                          # Unit tests
    ├── example
    │   ├── __init__.py            # Test example package initialization
    │   └── test_example.py        # Example unit tests
    └── __init__.py                # Tests initialization
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
