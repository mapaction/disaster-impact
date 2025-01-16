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

run_monty:
	@echo "Running the application.."
	@poetry run python -m src.monty_flatten_scripts_download.download_process_monty_data

run_cerf:
	@echo "Running the application.."
	@poetry run python -m src.cerf_etl.cerf_downloader

run_cgt:
	@echo "Running the application.."
	@poetry run python -m src.cgt.cgt_etl

run_gdacs:
	@echo "Running the application.."
	@poetry run python -m src.gdacs.gdacs_search_fetcher

run_glide:
	@echo "Running the application.."
	@poetry run python -m src.glide.download_v2_automated

run_adam:
	@echo "Running the application.."
	@poetry run python -m src.adam.wfp_adam_downloader

run_adam_hdx:
	@echo "Running the application.."
	@poetry run python -m src.adam.wfp_hdx

run_glide_exploration:
	@echo "Running the application.."
	@poetry run python -m src.glide.data_standardisation_glide

run_glide_consolidation:
	@echo "Running the application.."
	@poetry run python -m src.glide.data_consolidation_glide

run_gdacs_exploration:
	@echo "Running the application.."
	@poetry run python -m src.gdacs.data_standardisation_gdacs

run_gdacs_consolidation:
	@echo "Running the application.."
	@poetry run python -m src.gdacs.data_consolidation_gdacs

run_dc_exploration:
	@echo "Running the application.."
	@poetry run python -m src.cgt.data_standardisation_dc

run_dc_consolidation:
	@echo "Running the application.."
	@poetry run python -m src.cgt.data_consolidation_dc

help:
	@echo "Available make commands for setup:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"
	@echo ""

run_glide_normal:
	@echo "Running the application.."
	@poetry run python -m src.glide.data_normalisation_glide

run_gdacs_normal:
	@echo "Running the application.."
	@poetry run python -m src.gdacs.data_normalisation_gdacs

run_dc_normal:
	@echo "Running the application.."
	@poetry run python -m src.disaster_charter.data_normalisation_dis_chart

run_emdat_normal:
	@echo "Running the application.."
	@poetry run python -m src.emdat.data_normalisation_emdat

run_idmc_normal:
	@echo "Running the application.."
	@poetry run python -m src.idmc.data_normalisation_idmc