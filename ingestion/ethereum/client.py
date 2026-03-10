from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ingestion.common.config import get_settings
from ingestion.common.logging import get_logger

logger = get_logger(__name__)


class EthereumRpcClient:
    def __init__(self, rpc_url: str | None = None, timeout: float = 30.0) -> None:
        settings = get_settings()
        self.rpc_url = rpc_url or settings.ethereum_rpc_url
        self._client = httpx.Client(timeout=timeout)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _call(self, method: str, params: list[Any]) -> Any:
        response = self._client.post(
            self.rpc_url,
            json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"Ethereum RPC error for {method}: {payload['error']}")
        return payload["result"]

    def get_latest_block_number(self) -> int:
        return int(self._call("eth_blockNumber", []), 16)

    def get_block_by_number(
        self,
        block_number: int,
        full_transactions: bool = False,
    ) -> dict[str, Any]:
        result = self._call("eth_getBlockByNumber", [hex(block_number), full_transactions])
        if result is None:
            raise RuntimeError(f"Block {block_number} not found")
        return result

    def get_transaction_receipt(self, transaction_hash: str) -> dict[str, Any]:
        result = self._call("eth_getTransactionReceipt", [transaction_hash])
        if result is None:
            raise RuntimeError(f"Transaction receipt {transaction_hash} not found")
        return result

    @staticmethod
    def hex_to_int(value: str | None) -> int | None:
        if value is None:
            return None
        return int(value, 16)

    @staticmethod
    def hex_timestamp_to_datetime(value: str) -> datetime:
        return datetime.fromtimestamp(int(value, 16), tz=UTC)

    def close(self) -> None:
        self._client.close()
