select
    transaction_hash,
    block_number,
    block_hash,
    transaction_index,
    lower(from_address) as from_address,
    lower(to_address) as to_address,
    value_wei::numeric(38, 0) as value_wei,
    gas::numeric(38, 0) as gas_limit,
    gas_price::numeric(38, 0) as gas_price,
    max_fee_per_gas::numeric(38, 0) as max_fee_per_gas,
    max_priority_fee_per_gas::numeric(38, 0) as max_priority_fee_per_gas,
    receipt_gas_used::numeric(38, 0) as receipt_gas_used,
    receipt_effective_gas_price::numeric(38, 0) as receipt_effective_gas_price,
    status,
    transaction_timestamp at time zone 'utc' as transaction_timestamp_utc,
    date_trunc('day', transaction_timestamp at time zone 'utc')::date as transaction_date,
    ingested_at
from {{ ref('bronze_transactions') }}

