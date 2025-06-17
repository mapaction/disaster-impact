.PHONY: all
all = help

.venv:
	@echo "Installing project dependencies.."
	@poetry install --no-root


hooks:
	@echo "Adding pre-commit hooks.."
	@poetry run pre-commit install
	

test:
	@echo "Running unit tests.."
	@poetry run pytest

lint:
	@echo "Running lint tests.."
	@poetry run pre-commit run --all-files

clean:
	@echo "Removing .venv"
	@rm -rf .venv
	@poetry env remove --all

run_gdacs_download:
	@echo "Running GDACS download"
	@poetry run python -m src.gdacs.data_acquisition_api

run_glide_download:
	@echo "Running Glide download"
	@poetry run python -m src.glide.data_acquisition_scrape

run_cerf_download:
	@echo "Running CERF download"
	@poetry run python -m src.cerf.data_acquisition_scrape

run_disaster_charter_download:
	@echo "Running Disaster-Charter download"
	@poetry run python -m src.disaster_charter.data_acquisition_scrape

run_idus_download:
	@echo "Downloading IDUS dump → data/idmc_idu/idus_all.json"
	@mkdir -p data/idmc_idu
	@curl -L --compressed \
		-o data/idmc_idu/idus_all.json \
		"https://helix-copilot-prod-helix-media-external.s3.amazonaws.com/external-media/api-dump/idus-all/2025-06-04-10-00-32/5mndO/idus_all.json"
	@echo "✅  Saved (decompressed): data/idmc_idu/idus_all.json"

run_all_download: | run_gdacs_download run_glide_download run_cerf_download run_disaster_charter_download run_idus_download
	@echo "Running all download scripts.."

help:
	@echo "Available make commands for setup:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"
	@echo " make run_all_normal - Run all normalisation scripts"
	@echo " make run_all_clean  - Run all normalisation and cleaner scripts"
	@echo ""