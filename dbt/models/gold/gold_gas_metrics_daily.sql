select
    transaction_date,
    count(*) as transaction_count,
    sum(receipt_gas_used) as total_gas_used,
    avg(receipt_gas_used) as avg_gas_used,
    avg(receipt_effective_gas_price) as avg_effective_gas_price
from {{ ref('silver_transactions') }}
group by 1

