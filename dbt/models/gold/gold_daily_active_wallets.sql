with wallets as (
    select
        transaction_date,
        from_address as wallet_address
    from {{ ref('silver_transactions') }}
    union
    select
        transaction_date,
        to_address as wallet_address
    from {{ ref('silver_transactions') }}
    where to_address is not null
)
select
    transaction_date as activity_date,
    count(distinct wallet_address) as daily_active_wallets
from wallets
group by 1

