"""PostgreSQL adapter for the Treatment Plan repository seam."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .migration import MigrationRunner
from .repository import RuntimeRecord
from .retention import RetentionPolicy, RetentionResult, apply_retention


class PostgreSQLRepository:
    def __init__(
        self,
        dsn: str,
        migrations: Path | None = None,
        connect: Callable[[str], Any] | None = None,
    ) -> None:
        if not dsn.strip():
            raise ValueError("PostgreSQL DSN is required")
        self.dsn = dsn
        self.migrations = migrations or Path(__file__).with_name("migrations")
        self._connect_factory = connect

    def _connect(self) -> Any:
        if self._connect_factory is not None:
            return self._connect_factory(self.dsn)
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - exercised by deployment packaging
            raise RuntimeError(
                "PostgreSQL support requires the 'psycopg[binary]' dependency"
            ) from exc
        return psycopg.connect(self.dsn)

    def migrate(self) -> tuple[str, ...]:
        with closing(self._connect()) as connection:
            return MigrationRunner(self.migrations, "postgres").migrate(connection)

    def rollback(self, steps: int | None = None) -> tuple[str, ...]:
        with closing(self._connect()) as connection:
            return MigrationRunner(self.migrations, "postgres").rollback(connection, steps)

    def ping(self) -> bool:
        try:
            with closing(self._connect()) as connection:
                connection.execute("SELECT 1")
            return True
        except Exception:
            return False

    def put(self, record: RuntimeRecord) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                "INSERT INTO runtime_records(key, value) VALUES (%s, %s) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (record.key, record.value),
            )
            connection.commit()

    def get(self, key: str) -> RuntimeRecord | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT key, value FROM runtime_records WHERE key = %s", (key,)
            ).fetchone()
        return RuntimeRecord(*row) if row else None

    def apply_retention(
        self, policy: RetentionPolicy, now: datetime
    ) -> RetentionResult:
        with closing(self._connect()) as connection:
            return apply_retention(connection, "postgres", policy, now)


PostgresRepository = PostgreSQLRepository
