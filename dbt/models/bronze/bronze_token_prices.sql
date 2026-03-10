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
    total_volume,
    raw_payload,
    ingested_at
from {{ source('raw', 'bronze_token_prices') }}

