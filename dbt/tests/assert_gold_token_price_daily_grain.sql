select
    asset_id,
    price_date,
    vs_currency,
    count(*) as row_count
from {{ ref('gold_token_price_daily') }}
group by 1, 2, 3
having count(*) > 1
