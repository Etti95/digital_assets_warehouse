# Architecture Decisions

## Use Postgres for the MVP Warehouse

Postgres is the most practical local-first choice for a portfolio project. It supports SQL modeling, dbt, and idempotent ingestion patterns without introducing cloud dependencies too early.

Tradeoff:
It is not the ideal long-term engine for very large on-chain workloads, but it is sufficient for demonstrating platform design and analytics engineering fundamentals.

## Keep the Initial Scope Narrow

The MVP focuses on Ethereum blocks, Ethereum transactions, and token prices. This is enough to demonstrate ingestion, warehouse modeling, orchestration, testing, and documentation while keeping the project understandable for reviewers.

Tradeoff:
The analytics surface is intentionally narrow. More complex domains such as token transfers, NFT activity, and labeling are deferred until the pipeline foundation is stable.

## Choose Batch Ingestion Over Streaming

Daily batch jobs are easier to reason about, operate, and explain in a portfolio repository. They also align with the Bronze to Gold pattern used in the project.

Tradeoff:
This does not capture real-time analytics use cases. The codebase is structured so streaming can be introduced later without reorganizing the entire repo.

## Use Raw Payload Retention in Bronze

Bronze tables retain JSON payloads alongside selected parsed columns. This gives the warehouse both reproducibility and flexibility for future model expansion.

Tradeoff:
Storage use is higher, but the upside is better debuggability and easier schema evolution for blockchain payloads.

## Use Airflow Locally

Airflow is heavier than lightweight task runners, but it is still the clearest production-style orchestration choice for the target audience.

Tradeoff:
It adds local complexity. Docker Compose and a focused DAG keep that complexity bounded for the MVP.

