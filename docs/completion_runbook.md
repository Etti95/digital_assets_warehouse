# Completion Runbook

This document gives a step-by-step path for taking `crypto-data-warehouse` from its current MVP state to a more complete, polished portfolio project.

## 1. Prepare the Local Environment

1. Confirm Docker Desktop is running.
2. Confirm `uv` is installed by running `uv --version`.
3. Confirm Python 3.11+ is available.
4. Review [.env.example](/Users/richmore/Desktop/projects/crypto-data-warehouse/.env.example).
5. Copy `.env.example` to `.env` if you want to reset your local config.
6. Keep `POSTGRES_PORT=5433` unless you intentionally want a different host port.
7. Set `ETHEREUM_RPC_URL` to your preferred RPC endpoint if you do not want to use the default public node.

## 2. Install Dependencies

1. Run `uv sync --dev`.
2. Confirm the virtual environment was created at `.venv/`.
3. Run `.venv/bin/pytest`.
4. Run `.venv/bin/ruff check .`.
5. If either command fails, fix those issues before moving on.

## 3. Start the Local Stack

1. Run `docker compose up -d postgres airflow-webserver airflow-scheduler`.
2. Run `docker compose run --rm airflow-init`.
3. Run `docker compose ps`.
4. Confirm:
   - `postgres` is `healthy`
   - `airflow-webserver` is `Up`
   - `airflow-scheduler` is `Up`
5. Open Airflow at `http://localhost:8080`.
6. Sign in with `admin` / `admin` unless you change the bootstrap credentials.

## 4. Verify Raw Warehouse Initialization

1. Run:
   ```bash
   docker exec crypto-warehouse-postgres psql -U crypto -d crypto_warehouse -c "\dt"
   ```
2. Confirm these tables exist:
   - `bronze_blocks`
   - `bronze_transactions`
   - `bronze_token_prices`

## 5. Run Ingestion Manually

This is the fastest way to confirm the pipeline works before relying on Airflow scheduling.

1. Run market ingestion:
   ```bash
   docker compose exec airflow-webserver bash -lc 'cd /opt/airflow/project && python -m ingestion.market.fetch_prices'
   ```
2. Run a small block backfill first:
   ```bash
   docker compose exec airflow-webserver bash -lc 'cd /opt/airflow/project && ETHEREUM_BACKFILL_BLOCKS=2 python -m ingestion.ethereum.fetch_blocks'
   ```
3. Run transaction ingestion:
   ```bash
   docker compose exec airflow-webserver bash -lc 'cd /opt/airflow/project && python -m ingestion.ethereum.fetch_transactions'
   ```
4. Check row counts:
   ```bash
   docker exec crypto-warehouse-postgres psql -U crypto -d crypto_warehouse -c "select count(*) from bronze_blocks;"
   docker exec crypto-warehouse-postgres psql -U crypto -d crypto_warehouse -c "select count(*) from bronze_transactions;"
   docker exec crypto-warehouse-postgres psql -U crypto -d crypto_warehouse -c "select count(*) from bronze_token_prices;"
   ```
5. If transaction ingestion is too slow, keep the block backfill small until performance improvements are made.

## 6. Build and Test the dbt Layer

1. Run:
   ```bash
   docker compose exec airflow-webserver bash -lc 'cd /opt/airflow/project/dbt && dbt run --profiles-dir /opt/airflow/project/dbt'
   ```
2. Then run:
   ```bash
   docker compose exec airflow-webserver bash -lc 'cd /opt/airflow/project/dbt && dbt test --profiles-dir /opt/airflow/project/dbt'
   ```
3. Confirm all models build successfully.
4. Confirm all tests pass.
5. Check Gold table counts:
   ```bash
   docker exec crypto-warehouse-postgres psql -U crypto -d crypto_warehouse -c "select 'gold_daily_active_wallets' as table_name, count(*) as row_count from analytics_analytics.gold_daily_active_wallets union all select 'gold_transactions_per_day', count(*) from analytics_analytics.gold_transactions_per_day union all select 'gold_gas_metrics_daily', count(*) from analytics_analytics.gold_gas_metrics_daily union all select 'gold_token_price_daily', count(*) from analytics_analytics.gold_token_price_daily;"
   ```

## 7. Validate the Airflow DAG

1. Open Airflow and locate the `crypto_pipeline` DAG.
2. Unpause the DAG.
3. Trigger a manual run.
4. Watch task execution in this order:
   - `ingest_ethereum_blocks`
   - `ingest_ethereum_transactions`
   - `ingest_market_prices`
   - `dbt_run`
   - `dbt_test`
5. Review task logs for any environment or connection issues.
6. Confirm data appears in Bronze and Gold after the DAG finishes.

## 8. Complete the Remaining Engineering Work

These are the highest-value next implementation steps.

1. Improve ingestion performance.
   - Batch RPC calls where possible.
   - Consider block and receipt fetch concurrency with rate-limit awareness.
   - Add a configurable max-block window for a single run.
2. Improve ingestion reliability.
   - Add stronger resume semantics for partially loaded blocks.
   - Add explicit dead-letter or failure logging guidance.
   - Add more integration tests around Postgres writes.
3. Improve orchestration quality.
   - Make Airflow tasks parameterizable for backfills.
   - Add retry and timeout settings per task.
   - Add a health-check task or sensor pattern if needed.
4. Improve dbt modeling.
   - Add model-level docs for more columns.
   - Consider incremental models once the backfill size grows.
   - Add additional Gold marts for chain activity and wallet behavior.
5. Improve portfolio presentation.
   - Add sample screenshots of Airflow and warehouse outputs to the README.
   - Add an example dashboard or BI layer in [dashboards/README.md](/Users/richmore/Desktop/projects/crypto-data-warehouse/dashboards/README.md).
   - Add a short demo walkthrough section in [README.md](/Users/richmore/Desktop/projects/crypto-data-warehouse/README.md).

## 9. Recommended Order to Finish the Project

Follow this order if your goal is a polished portfolio-ready repo:

1. Stabilize manual ingestion and Airflow DAG runs.
2. Add integration tests for DB writes and DAG task behavior.
3. Improve ingestion performance for larger historical windows.
4. Add one more meaningful analytics domain such as ERC-20 transfers.
5. Add one small dashboard or notebook-driven demo artifact.
6. Add CI to run lint, pytest, and dbt checks automatically.
7. Add deployment notes for cloud migration paths.

## 10. Definition of Done

You can consider the project complete for a strong portfolio MVP when all of the following are true:

1. A reviewer can clone the repo and get it running locally with the README.
2. The Airflow DAG runs successfully without manual intervention.
3. Bronze, Silver, and Gold layers populate with real data.
4. `pytest`, Ruff, `dbt run`, and `dbt test` pass reliably.
5. The README explains the architecture and tradeoffs clearly.
6. The repo includes at least one downstream demonstration artifact such as a dashboard, notebook, or screenshots.
7. The next-stage roadmap is visible but the current scope feels complete and intentional.

## 11. Suggested Immediate Next Action

If you want the shortest path forward, do this next:

1. Trigger the `crypto_pipeline` DAG in Airflow.
2. Confirm a successful full DAG run.
3. Add one integration test for ingestion-to-Postgres behavior.
4. Add one lightweight dashboard artifact for the Gold tables.
