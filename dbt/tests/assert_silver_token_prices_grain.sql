select
    asset_id,
    price_date,
    vs_currency,
    count(*) as row_count
from {{ ref('silver_token_prices') }}
group by 1, 2, 3
having count(*) > 1

