-- Demo queries for portfolio walkthroughs.

select *
from analytics_analytics.gold_daily_active_wallets
order by activity_date desc
limit 5;

select *
from analytics_analytics.gold_transactions_per_day
order by transaction_date desc
limit 5;

select *
from analytics_analytics.gold_gas_metrics_daily
order by transaction_date desc
limit 5;

select
    asset_id,
    price_date,
    close_price,
    market_cap,
    total_volume
from analytics_analytics.gold_token_price_daily
order by price_date desc, asset_id
limit 10;
