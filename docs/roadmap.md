# Roadmap

## Phase 1: MVP Foundation

- Local Postgres warehouse and Airflow orchestration
- Ethereum blocks and transactions ingestion
- Daily token price ingestion
- Bronze, Silver, Gold dbt models
- Basic automated tests and repo documentation

## Phase 2: Broader Chain Coverage

- Add Polygon, Arbitrum, and Base ingestion modules
- Introduce chain dimension tables and multi-chain model patterns
- Support chain-aware Gold metrics

## Phase 3: Richer Analytics

- Token transfer and ERC-20 event ingestion
- Wallet labeling and entity enrichment
- Counterparty segmentation and cohort metrics
- Entity clustering experiments

## Phase 4: Platform Maturity

- CI/CD for tests, linting, and dbt validation
- Data quality monitoring and alerting
- Incremental loading optimization and backfill tooling
- Cloud deployment patterns for managed Postgres or warehouses

## Phase 5: Advanced Serving

- API layer for reusable metrics access
- Dashboard implementations for portfolio demos
- Streaming ingestion patterns with Kafka or similar tooling
- Research-friendly semantic layer and metric definitions

