select
    block_number,
    block_hash,
    parent_hash,
    block_timestamp at time zone 'utc' as block_timestamp_utc,
    date_trunc('day', block_timestamp at time zone 'utc')::date as block_date,
    lower(miner_address) as miner_address,
    gas_limit::numeric(38, 0) as gas_limit,
    gas_used::numeric(38, 0) as gas_used,
    base_fee_per_gas::numeric(38, 0) as base_fee_per_gas,
    transaction_count,
    ingested_at
from {{ ref('bronze_blocks') }}

