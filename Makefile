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

run_glide_normal:
	@echo "Running Glide normalisation"
	@poetry run python -m src.glide.data_normalisation_glide

run_gdacs_normal:
	@echo "Running GDACS normalisation"
	@poetry run python -m src.gdacs.data_normalisation_gdacs

run_dc_normal:
	@echo "Running Disaster-Charter normalisation"
	@poetry run python -m src.disaster_charter.data_normalisation_dc

run_emdat_normal:
	@echo "Running EmDat normalisation"
	@poetry run python -m src.emdat.data_normalisation_emdat

run_idmc_normal:
	@echo "Running IDMC normalisation"
	@poetry run python -m src.idmc.data_normalisation_idmc

run_cerf_normal:
	@echo "Running CERF normalisation"
	@poetry run python -m src.cerf.data_normalisation_cerf

run_ifrc_normal:
	@echo "Running IFRC normalisation"
	@poetry run python -m src.ifrc_eme.data_normalisation_ifrc_eme

run_all_normal: | run_glide_normal run_gdacs_normal run_dc_normal run_emdat_normal run_idmc_normal run_cerf_normal run_ifrc_normal
	@echo "Running all normalisation scripts.."

run_all_clean: | run_all_normal
	@echo "Running all cleaning scripts.."
	@poetry run python -m src.utils.splitter

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