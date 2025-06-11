# Disaster Impact Database

The **Disaster Impact Database** is an open‑source initiative that collects, cleans, and harmonises disaster‑related data from multiple global providers. It produces a unified, analysis‑ready dataset that supports the Anticipatory Action Framework and broader humanitarian research.

> Supported sources: **GDACS · GLIDE · CERF · EM‑DAT · IDMC · IFRC‑DREF · Disaster Charter**

---

## Key Goals

- **Automated downloads** of raw data where APIs exist.
- **Headless scraping** for semi‑automated sources.
- **Normalisation** into consistent, JSON‑schema‑validated tables (**under development**).
- **Export** of tidy CSVs for each provider.
- **Event matching** across feeds by hazard, country, and date (±7 days).
- **Exploratory analytics** that quantify overlap and uniqueness across sources.

---

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| **Python ≥ 3.10** | Core language |
| **Poetry** | Virtual‑env and dependency management |
| **Firefox** | Headless scraping engine |
| **GeckoDriver** | WebDriver interface for Firefox |
| **Unix‑like shell** | Tested on macOS, Linux, and Windows WSL2 |

> **Tip — GLIDE scraper profile**  
> The GLIDE portal occasionally shows CAPTCHAs. Edit `src/glide/data_acquisition_scrape.py` and set `FIREFOX_PROFILE` to the absolute path of a persistent Firefox profile (e.g. `~/.mozilla/firefox/abcd1234.default-release`).

---

## Quick Start

```bash
# 0  Install Poetry (skip if you already have it)
$ curl -sSL https://install.python-poetry.org | python3 -

# 1  Clone the repo and enter it
$ git clone https://github.com/mapaction/disaster-impact.git
$ cd disaster-impact

# 2  Create the virtual environment (Poetry will be installed if missing)
$ make .venv

# 3  Activate the environment (Poetry makes this automatic in new shells)
$ poetry shell
```

All Makefile targets below assume the environment is active.

---

## Data Acquisition

| Dataset | Access Method | Historical Coverage | Makefile Target | Status |
|---------|---------------|---------------------|-----------------|--------|
| **GDACS** | REST API | 2000 – present | `make run_gdacs_download` | Automated |
| **IDMC IDU** | REST API | 2016 – present | `make run_idus_download` | Automated |
| **GLIDE** | Headless scrape | 1930 – present | `make run_glide_scrape` | Semi‑automated |
| **CERF** | Headless scrape | 2006 – present | `make run_cerf_scrape` | Semi‑automated |
| **Disaster Charter** | Headless scrape | 2000 – present | `make run_charter_scrape` | Semi‑automated |
| **EM‑DAT** | Manual download | 2000 – present | — | Manual |
| **IFRC DREF** | Manual download | 2018 – present | — | Manual |

Raw files are stored in `data/<provider>/`, preserving provenance and update timestamps.

---

## Processing & Analysis Workflow

1. **Load** raw datasets (see `notebooks/process_sandbox.ipynb`).
2. **Pre‑process**: select columns, rename, parse dates, harmonise hazard labels.
3. **Match events** by hazard, ISO‑3 country code, and date window (±7 days).
4. **Generate analytics**: bar charts of retention/overlap and a chord diagram of pairwise matches.

The notebook is fully reproducible; rerun it after refreshing data to obtain an updated master table.

---

## Project Structure

```text
.
├── data/                # Raw datasets (one sub‑folder per provider)
├── docs/                # Additional documentation
├── notebooks/           # Jupyter notebooks for ETL and analysis
├── src/                 # Source code modules
│   ├── cerf/
│   ├── disaster_charter/
│   ├── emdat/
│   ├── gdacs/
│   ├── glide/
│   ├── idmc/
│   ├── ifrc_dref/
│   ├── unified/         # Unified schema & helpers
│   └── utils/
├── static_data/         # Reference tables (e.g., country & hazard codes)
├── tests/               # Unit & integration tests
├── Makefile             # Automation commands
├── pyproject.toml       # Project metadata
└── README.md            # This file
```

---

## Common Make Targets

| Target | Action |
|--------|--------|
| `.venv` | Bootstrap the Poetry virtual‑env |
| `test` | Run the test suite (`pytest`) |
| `lint` | Run `ruff` and `mypy` checks |
| `clean` | Remove virtual‑env, caches & temporary files |
| `run_<source>_download` | Refresh a specific feed (see table above) |

---

## Limitations & Roadmap

- **Matching logic** is intentionally conservative; multi‑country or slow‑onset events may be under‑linked.
- **ETL pipeline** is notebook‑driven; migration to a parametric workflow (e.g., Airflow, Dagster) is planned.
- **Manual feeds** (EM‑DAT, IFRC‑DREF) need scripted ingestion once stable APIs become available.
- **Funding gap** stalled development after the HNPW 2025 demo; contributions are welcome to resume full ETL work.

---

## Contributing

1. Fork the repository and create a feature branch from `main`.
2. Commit logical, well‑documented changes.
3. Ensure `make test lint` passes.
4. Open a pull request; the CI pipeline will run automatically.

---

## License

Distributed under the **GNU GPL v3**. See the [LICENSE](LICENSE) file for details.

---

## Author

**Evangelos Diakatos** · ediakatos@mapaction.org

---

*Happy coding & stay safe!*

