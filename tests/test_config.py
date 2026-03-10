from ingestion.common.config import Settings


def test_settings_parses_asset_ids() -> None:
    settings = Settings(
        ETHEREUM_RPC_URL="https://rpc.example",
        COINGECKO_ASSET_IDS="ethereum, bitcoin ,solana",
    )

    assert settings.asset_ids == ["ethereum", "bitcoin", "solana"]


def test_postgres_dsn_is_constructed() -> None:
    settings = Settings(
        ETHEREUM_RPC_URL="https://rpc.example",
        POSTGRES_USER="alice",
        POSTGRES_PASSWORD="secret",
        POSTGRES_HOST="db",
        POSTGRES_PORT=5433,
        POSTGRES_DB="warehouse",
    )

    assert settings.postgres_dsn == "postgresql://alice:secret@db:5433/warehouse"

