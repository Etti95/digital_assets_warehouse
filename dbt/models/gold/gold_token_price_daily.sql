select
    asset_id,
    symbol,
    price_date,
    vs_currency,
    open_price,
    high_price,
    low_price,
    close_price,
    market_cap,
    total_volume
from {{ ref('silver_token_prices') }}

