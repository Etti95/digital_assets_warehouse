from ingestion.ethereum.fetch_blocks import build_block_record
from ingestion.ethereum.fetch_transactions import build_transaction_record
from ingestion.market.fetch_prices import normalize_market_chart


class StubClient:
    @staticmethod
    def hex_to_int(value: str | None) -> int | None:
        if value is None:
            return None
        return int(value, 16)

    @staticmethod
    def hex_timestamp_to_datetime(value: str):
        from datetime import UTC, datetime

        return datetime.fromtimestamp(int(value, 16), tz=UTC)


def test_build_block_record() -> None:
    record = build_block_record(
        StubClient(),
        {
            "number": hex(123),
            "hash": "0xabc",
            "parentHash": "0xdef",
            "timestamp": hex(1_700_000_000),
            "miner": "0xminer",
            "gasLimit": hex(30_000_000),
            "gasUsed": hex(21_000),
            "baseFeePerGas": hex(100),
            "transactions": ["0x1", "0x2"],
        },
    )

    assert record["block_number"] == 123
    assert record["transaction_count"] == 2


def test_build_transaction_record() -> None:
    record = build_transaction_record(
        StubClient(),
        {"timestamp": hex(1_700_000_000)},
        {
            "hash": "0xhash",
            "blockNumber": hex(123),
            "blockHash": "0xblock",
            "transactionIndex": hex(0),
            "from": "0xfrom",
            "to": "0xto",
            "value": hex(42),
            "gas": hex(21_000),
            "gasPrice": hex(100),
            "maxFeePerGas": hex(100),
            "maxPriorityFeePerGas": hex(2),
        },
        {
            "gasUsed": hex(21_000),
            "effectiveGasPrice": hex(90),
            "status": hex(1),
        },
    )

    assert record["transaction_hash"] == "0xhash"
    assert record["status"] == 1


def test_normalize_market_chart() -> None:
    records = normalize_market_chart(
        "ethereum",
        {
            "prices": [[1_700_000_000_000, 2000.0], [1_700_086_400_000, 2100.0]],
            "market_caps": [[1_700_000_000_000, 100.0], [1_700_086_400_000, 101.0]],
            "total_volumes": [[1_700_000_000_000, 10.0], [1_700_086_400_000, 11.0]],
        },
    )

    assert len(records) == 2
    assert records[1]["open_price"] == 2000.0

