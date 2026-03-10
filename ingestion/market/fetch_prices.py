import json
from collections.abc import Iterable
from datetime import UTC, datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ingestion.common.config import get_settings
from ingestion.common.db import execute_batch
from ingestion.common.logging import get_logger

logger = get_logger(__name__)

UPSERT_PRICES_SQL = """
insert into bronze_token_prices (
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
    raw_payload
) values (
    %(asset_id)s,
    %(symbol)s,
    %(price_date)s,
    %(vs_currency)s,
    %(open_price)s,
    %(high_price)s,
    %(low_price)s,
    %(close_price)s,
    %(market_cap)s,
    %(total_volume)s,
    %(raw_payload)s::jsonb
)
on conflict (asset_id, price_date, vs_currency) do update set
    symbol = excluded.symbol,
    open_price = excluded.open_price,
    high_price = excluded.high_price,
    low_price = excluded.low_price,
    close_price = excluded.close_price,
    market_cap = excluded.market_cap,
    total_volume = excluded.total_volume,
    raw_payload = excluded.raw_payload,
    ingested_at = now();
"""


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
def fetch_market_chart(asset_id: str) -> dict:
    settings = get_settings()
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{settings.coingecko_api_url}/coins/{asset_id}/market_chart",
            params={
                "vs_currency": settings.price_vs_currency,
                "days": settings.price_lookback_days,
                "interval": "daily",
            },
        )
        response.raise_for_status()
        return response.json()


def normalize_market_chart(asset_id: str, payload: dict) -> list[dict]:
    settings = get_settings()
    prices = payload.get("prices", [])
    market_caps = {
        datetime.fromtimestamp(item[0] / 1000, tz=UTC).date(): item[1]
        for item in payload.get("market_caps", [])
    }
    volumes = {
        datetime.fromtimestamp(item[0] / 1000, tz=UTC).date(): item[1]
        for item in payload.get("total_volumes", [])
    }

    normalized = []
    previous_close = None
    for timestamp_ms, close_price in prices:
        price_date = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).date()
        normalized.append(
            {
                "asset_id": asset_id,
                "symbol": asset_id,
                "price_date": price_date,
                "vs_currency": settings.price_vs_currency,
                "open_price": previous_close,
                "high_price": close_price,
                "low_price": close_price,
                "close_price": close_price,
                "market_cap": market_caps.get(price_date),
                "total_volume": volumes.get(price_date),
                "raw_payload": json.dumps(
                    {
                        "price": close_price,
                        "market_cap": market_caps.get(price_date),
                        "total_volume": volumes.get(price_date),
                        "price_date": price_date.isoformat(),
                    }
                ),
            }
        )
        previous_close = close_price
    return normalized


def fetch_prices(asset_ids: list[str] | None = None) -> list[dict]:
    settings = get_settings()
    selected_assets = asset_ids or settings.asset_ids
    records = []
    for asset_id in selected_assets:
        logger.info("Fetching daily market prices for %s", asset_id)
        payload = fetch_market_chart(asset_id)
        records.extend(normalize_market_chart(asset_id, payload))
    return records


def load_prices(records: Iterable[dict]) -> None:
    execute_batch(UPSERT_PRICES_SQL, records)


def main() -> None:
    records = fetch_prices()
    load_prices(records)
    logger.info("Loaded %s market price records", len(records))


if __name__ == "__main__":
    main()
