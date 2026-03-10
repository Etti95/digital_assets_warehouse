from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

from ingestion.common.config import get_settings


@contextmanager
def get_connection():
    settings = get_settings()
    with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as connection:
        yield connection


def execute_batch(statement: str, records: Iterable[dict[str, Any]]) -> None:
    payload = list(records)
    if not payload:
        return

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(statement, payload)
        connection.commit()


def fetch_one(statement: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, params or {})
            return cursor.fetchone()

