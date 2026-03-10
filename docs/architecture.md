# Architecture

## Overview

`digital-assets-warehouse` is a local-first analytics stack for crypto and on-chain data. The MVP ingests Ethereum blocks, Ethereum transactions, and daily token prices into Postgres, transforms them with dbt, and orchestrates the flow with Airflow.

## System Design

The architecture is intentionally simple:

- Python ingestion jobs call Ethereum JSON-RPC and a public market API.
- Raw data lands in Postgres bronze tables with idempotent upserts.
- dbt transforms the raw tables into Silver normalization models and Gold analytics marts.
- Airflow runs ingestion, transformation, and data quality tasks in a clear daily DAG.
- Docker Compose provides a reproducible local environment for Postgres and Airflow.

## Bronze, Silver, Gold

The warehouse follows a layered modeling pattern:

- Bronze stores raw operational records with minimal shaping and retained payload JSON.
- Silver standardizes timestamps, types, address casing, and grains.
- Gold exposes analyst-friendly daily metrics for wallet activity, transactions, gas usage, and token prices.

This structure keeps ingestion logic simple while making downstream analytics predictable and easier to test.

## Why This Stack

- `Python 3.11` is a practical choice for API ingestion, testing, and orchestration tasks.
- `Postgres` is accessible for local development but still realistic for warehouse-style modeling.
- `dbt` expresses transformations and tests in a way that mirrors modern analytics engineering teams.
- `Airflow` demonstrates production-style orchestration without assuming a cloud control plane.
- `Docker Compose` makes the project runnable by reviewers without requiring managed infrastructure.

## Extensibility

The project is organized so it can later support:

- additional EVM chains with shared client abstractions
- alternative warehouses such as DuckDB, BigQuery, or Snowflake
- event streaming or Kafka-based ingestion
- wallet labeling and entity enrichment
- serving layers for APIs or dashboard applications
