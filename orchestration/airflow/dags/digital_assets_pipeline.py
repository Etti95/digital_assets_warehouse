from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_ROOT = Path("/opt/airflow/project")

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
}

with DAG(
    dag_id="digital_assets_pipeline",
    description="Local MVP digital assets warehouse pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["crypto", "warehouse", "portfolio"],
) as dag:
    ingest_blocks = BashOperator(
        task_id="ingest_ethereum_blocks",
        cwd=str(PROJECT_ROOT),
        bash_command="python -m ingestion.ethereum.fetch_blocks",
    )

    ingest_transactions = BashOperator(
        task_id="ingest_ethereum_transactions",
        cwd=str(PROJECT_ROOT),
        bash_command="python -m ingestion.ethereum.fetch_transactions",
    )

    ingest_prices = BashOperator(
        task_id="ingest_market_prices",
        cwd=str(PROJECT_ROOT),
        bash_command="python -m ingestion.market.fetch_prices",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        cwd=str(PROJECT_ROOT / "dbt"),
        bash_command="dbt run --profiles-dir /opt/airflow/project/dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        cwd=str(PROJECT_ROOT / "dbt"),
        bash_command="dbt test --profiles-dir /opt/airflow/project/dbt",
    )

    ingest_blocks >> ingest_transactions
    [ingest_transactions, ingest_prices] >> dbt_run >> dbt_test
