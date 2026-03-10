select
    asset_id,
    symbol,
    price_date,
    vs_currency,
    open_price::numeric(18, 8) as open_price,
    high_price::numeric(18, 8) as high_price,
    low_price::numeric(18, 8) as low_price,
    close_price::numeric(18, 8) as close_price,
    market_cap::numeric(24, 2) as market_cap,
    total_volume::numeric(24, 2) as total_volume,
    ingested_at
from {{ ref('bronze_token_prices') }}

