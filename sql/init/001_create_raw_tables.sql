create table if not exists bronze_blocks (
    block_number bigint primary key,
    block_hash text not null,
    parent_hash text not null,
    block_timestamp timestamptz not null,
    miner_address text,
    gas_limit numeric(38, 0),
    gas_used numeric(38, 0),
    base_fee_per_gas numeric(38, 0),
    transaction_count integer not null,
    raw_payload jsonb not null,
    ingested_at timestamptz not null default now()
);

create table if not exists bronze_transactions (
    transaction_hash text primary key,
    block_number bigint not null,
    block_hash text not null,
    transaction_index integer not null,
    from_address text not null,
    to_address text,
    value_wei numeric(38, 0) not null,
    gas numeric(38, 0),
    gas_price numeric(38, 0),
    max_fee_per_gas numeric(38, 0),
    max_priority_fee_per_gas numeric(38, 0),
    receipt_gas_used numeric(38, 0),
    receipt_effective_gas_price numeric(38, 0),
    status integer,
    transaction_timestamp timestamptz not null,
    raw_payload jsonb not null,
    ingested_at timestamptz not null default now()
);

create index if not exists idx_bronze_transactions_block_number
    on bronze_transactions (block_number);

create table if not exists bronze_token_prices (
    asset_id text not null,
    symbol text,
    price_date date not null,
    vs_currency text not null,
    open_price numeric(18, 8),
    high_price numeric(18, 8),
    low_price numeric(18, 8),
    close_price numeric(18, 8) not null,
    market_cap numeric(24, 2),
    total_volume numeric(24, 2),
    raw_payload jsonb not null,
    ingested_at timestamptz not null default now(),
    primary key (asset_id, price_date, vs_currency)
);

