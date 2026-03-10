select
    transaction_date,
    count(*) as transaction_count,
    count(distinct from_address) as distinct_senders,
    count(distinct to_address) as distinct_receivers
from {{ ref('silver_transactions') }}
group by 1

