PYTHON ?= .venv/bin/python
UV ?= uv
DBT_PROFILES_DIR ?= $(PWD)/dbt

.PHONY: install up down test lint format ingest-blocks ingest-transactions ingest-prices dbt-run dbt-test airflow-init

install:
	$(UV) sync --dev

up:
	docker compose up -d --build

down:
	docker compose down --remove-orphans

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

ingest-blocks:
	$(UV) run python -m ingestion.ethereum.fetch_blocks

ingest-transactions:
	$(UV) run python -m ingestion.ethereum.fetch_transactions

ingest-prices:
	$(UV) run python -m ingestion.market.fetch_prices

dbt-run:
	cd dbt && $(UV) run dbt run --profiles-dir $(DBT_PROFILES_DIR)

dbt-test:
	cd dbt && $(UV) run dbt test --profiles-dir $(DBT_PROFILES_DIR)

airflow-init:
	docker compose run --rm airflow-init

