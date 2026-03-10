select
    block_number,
    block_hash,
    parent_hash,
    block_timestamp,
    miner_address,
    gas_limit,
    gas_used,
    base_fee_per_gas,
    transaction_count,
    raw_payload,
    ingested_at
from {{ source('raw', 'bronze_blocks') }}

