import json
from collections.abc import Iterable

from ingestion.common.db import execute_batch, get_connection
from ingestion.common.logging import get_logger
from ingestion.ethereum.client import EthereumRpcClient

logger = get_logger(__name__)

UPSERT_TRANSACTIONS_SQL = """
insert into bronze_transactions (
    transaction_hash,
    block_number,
    block_hash,
    transaction_index,
    from_address,
    to_address,
    value_wei,
    gas,
    gas_price,
    max_fee_per_gas,
    max_priority_fee_per_gas,
    receipt_gas_used,
    receipt_effective_gas_price,
    status,
    transaction_timestamp,
    raw_payload
) values (
    %(transaction_hash)s,
    %(block_number)s,
    %(block_hash)s,
    %(transaction_index)s,
    %(from_address)s,
    %(to_address)s,
    %(value_wei)s,
    %(gas)s,
    %(gas_price)s,
    %(max_fee_per_gas)s,
    %(max_priority_fee_per_gas)s,
    %(receipt_gas_used)s,
    %(receipt_effective_gas_price)s,
    %(status)s,
    %(transaction_timestamp)s,
    %(raw_payload)s::jsonb
)
on conflict (transaction_hash) do update set
    block_number = excluded.block_number,
    block_hash = excluded.block_hash,
    transaction_index = excluded.transaction_index,
    from_address = excluded.from_address,
    to_address = excluded.to_address,
    value_wei = excluded.value_wei,
    gas = excluded.gas,
    gas_price = excluded.gas_price,
    max_fee_per_gas = excluded.max_fee_per_gas,
    max_priority_fee_per_gas = excluded.max_priority_fee_per_gas,
    receipt_gas_used = excluded.receipt_gas_used,
    receipt_effective_gas_price = excluded.receipt_effective_gas_price,
    status = excluded.status,
    transaction_timestamp = excluded.transaction_timestamp,
    raw_payload = excluded.raw_payload,
    ingested_at = now();
"""

PENDING_BLOCK_SQL = """
select b.block_number
from bronze_blocks b
where b.transaction_count > 0
  and not exists (
      select 1
      from bronze_transactions t
      where t.block_number = b.block_number
  )
order by b.block_number
"""


def fetch_pending_block_numbers() -> list[int]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(PENDING_BLOCK_SQL)
            return [row["block_number"] for row in cursor.fetchall()]


def build_transaction_record(
    client: EthereumRpcClient,
    block: dict,
    raw_transaction: dict,
    receipt: dict,
) -> dict:
    return {
        "transaction_hash": raw_transaction["hash"],
        "block_number": client.hex_to_int(raw_transaction["blockNumber"]),
        "block_hash": raw_transaction["blockHash"],
        "transaction_index": client.hex_to_int(raw_transaction["transactionIndex"]),
        "from_address": raw_transaction["from"],
        "to_address": raw_transaction.get("to"),
        "value_wei": client.hex_to_int(raw_transaction["value"]) or 0,
        "gas": client.hex_to_int(raw_transaction.get("gas")),
        "gas_price": client.hex_to_int(raw_transaction.get("gasPrice")),
        "max_fee_per_gas": client.hex_to_int(raw_transaction.get("maxFeePerGas")),
        "max_priority_fee_per_gas": client.hex_to_int(raw_transaction.get("maxPriorityFeePerGas")),
        "receipt_gas_used": client.hex_to_int(receipt.get("gasUsed")),
        "receipt_effective_gas_price": client.hex_to_int(receipt.get("effectiveGasPrice")),
        "status": client.hex_to_int(receipt.get("status")),
        "transaction_timestamp": client.hex_timestamp_to_datetime(block["timestamp"]),
        "raw_payload": json.dumps({"transaction": raw_transaction, "receipt": receipt}),
    }


def fetch_transactions(block_numbers: list[int] | None = None) -> list[dict]:
    pending_block_numbers = (
        block_numbers if block_numbers is not None else fetch_pending_block_numbers()
    )
    if not pending_block_numbers:
        logger.info("No transaction blocks pending ingestion")
        return []

    client = EthereumRpcClient()
    try:
        records = []
        logger.info("Fetching transactions for %s blocks", len(pending_block_numbers))
        for block_number in pending_block_numbers:
            block = client.get_block_by_number(block_number, full_transactions=True)
            for raw_transaction in block.get("transactions", []):
                receipt = client.get_transaction_receipt(raw_transaction["hash"])
                records.append(build_transaction_record(client, block, raw_transaction, receipt))
        return records
    finally:
        client.close()


def load_transactions(records: Iterable[dict]) -> None:
    execute_batch(UPSERT_TRANSACTIONS_SQL, records)


def main() -> None:
    records = fetch_transactions()
    load_transactions(records)
    logger.info("Loaded %s transaction records", len(records))


if __name__ == "__main__":
    main()
