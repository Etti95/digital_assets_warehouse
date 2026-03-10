select
    transaction_hash,
    block_number,
    block_hash,
    transaction_index,
    from_address,
    to_address,
    value_wei,
    gas,
    gas_price,
    max_fee_per_gas,
    max_priority_fee_per_gas,
    receipt_gas_used,
    receipt_effective_gas_price,
    status,
    transaction_timestamp,
    raw_payload,
    ingested_at
from {{ source('raw', 'bronze_transactions') }}

