from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="crypto_warehouse", alias="POSTGRES_DB")
    postgres_user: str = Field(default="crypto", alias="POSTGRES_USER")
    postgres_password: str = Field(default="crypto", alias="POSTGRES_PASSWORD")
    warehouse_schema: str = Field(default="public", alias="WAREHOUSE_SCHEMA")

    ethereum_rpc_url: str = Field(
        default="https://ethereum-rpc.publicnode.com",
        alias="ETHEREUM_RPC_URL",
    )
    ethereum_confirmation_depth: int = Field(default=6, alias="ETHEREUM_CONFIRMATION_DEPTH")
    ethereum_backfill_blocks: int = Field(default=25, alias="ETHEREUM_BACKFILL_BLOCKS")
    ethereum_start_block: int | None = Field(default=None, alias="ETHEREUM_START_BLOCK")

    coingecko_api_url: str = Field(
        default="https://api.coingecko.com/api/v3",
        alias="COINGECKO_API_URL",
    )
    coingecko_asset_ids: str = Field(default="ethereum,bitcoin", alias="COINGECKO_ASSET_IDS")
    price_lookback_days: int = Field(default=30, alias="PRICE_LOOKBACK_DAYS")
    price_vs_currency: str = Field(default="usd", alias="PRICE_VS_CURRENCY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("ethereum_start_block", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def asset_ids(self) -> list[str]:
        return [asset.strip() for asset in self.coingecko_asset_ids.split(",") if asset.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
