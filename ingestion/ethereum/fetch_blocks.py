import json
from collections.abc import Iterable

from ingestion.common.config import get_settings
from ingestion.common.db import execute_batch, fetch_one
from ingestion.common.logging import get_logger
from ingestion.ethereum.client import EthereumRpcClient

logger = get_logger(__name__)

UPSERT_BLOCKS_SQL = """
insert into bronze_blocks (
    block_number,
    block_hash,
    parent_hash,
    block_timestamp,
    miner_address,
    gas_limit,
    gas_used,
    base_fee_per_gas,
    transaction_count,
    raw_payload
) values (
    %(block_number)s,
    %(block_hash)s,
    %(parent_hash)s,
    %(block_timestamp)s,
    %(miner_address)s,
    %(gas_limit)s,
    %(gas_used)s,
    %(base_fee_per_gas)s,
    %(transaction_count)s,
    %(raw_payload)s::jsonb
)
on conflict (block_number) do update set
    block_hash = excluded.block_hash,
    parent_hash = excluded.parent_hash,
    block_timestamp = excluded.block_timestamp,
    miner_address = excluded.miner_address,
    gas_limit = excluded.gas_limit,
    gas_used = excluded.gas_used,
    base_fee_per_gas = excluded.base_fee_per_gas,
    transaction_count = excluded.transaction_count,
    raw_payload = excluded.raw_payload,
    ingested_at = now();
"""


def get_default_start_block(client: EthereumRpcClient) -> int:
    settings = get_settings()
    if settings.ethereum_start_block is not None:
        return settings.ethereum_start_block

    latest_confirmed_block = client.get_latest_block_number() - settings.ethereum_confirmation_depth
    max_loaded_block = fetch_one("select max(block_number) as block_number from bronze_blocks")
    if max_loaded_block and max_loaded_block["block_number"] is not None:
        return int(max_loaded_block["block_number"]) + 1

    return max(latest_confirmed_block - settings.ethereum_backfill_blocks + 1, 0)


def build_block_record(client: EthereumRpcClient, raw_block: dict) -> dict:
    return {
        "block_number": client.hex_to_int(raw_block["number"]),
        "block_hash": raw_block["hash"],
        "parent_hash": raw_block["parentHash"],
        "block_timestamp": client.hex_timestamp_to_datetime(raw_block["timestamp"]),
        "miner_address": raw_block.get("miner"),
        "gas_limit": client.hex_to_int(raw_block.get("gasLimit")),
        "gas_used": client.hex_to_int(raw_block.get("gasUsed")),
        "base_fee_per_gas": client.hex_to_int(raw_block.get("baseFeePerGas")),
        "transaction_count": len(raw_block.get("transactions", [])),
        "raw_payload": json.dumps(raw_block),
    }


def fetch_blocks(start_block: int | None = None, end_block: int | None = None) -> list[dict]:
    settings = get_settings()
    client = EthereumRpcClient()
    try:
        latest_confirmed_block = (
            client.get_latest_block_number() - settings.ethereum_confirmation_depth
        )
        resolved_start = start_block if start_block is not None else get_default_start_block(client)
        resolved_end = end_block if end_block is not None else latest_confirmed_block

        if resolved_start > resolved_end:
            logger.info("No blocks to ingest: start=%s end=%s", resolved_start, resolved_end)
            return []

        logger.info("Fetching Ethereum blocks from %s to %s", resolved_start, resolved_end)
        results = []
        for block_number in range(resolved_start, resolved_end + 1):
            raw_block = client.get_block_by_number(block_number, full_transactions=False)
            results.append(build_block_record(client, raw_block))
        return results
    finally:
        client.close()


def load_blocks(records: Iterable[dict]) -> None:
    execute_batch(UPSERT_BLOCKS_SQL, records)


def main() -> None:
    records = fetch_blocks()
    load_blocks(records)
    logger.info("Loaded %s block records", len(records))


if __name__ == "__main__":
    main()
