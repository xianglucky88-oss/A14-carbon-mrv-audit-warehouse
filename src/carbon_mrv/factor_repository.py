from __future__ import annotations

from .database import Database
from .models import FactorDefinition


class FactorRepository:
    def __init__(self, database: Database):
        self.conn = database.conn

    def save_many(self, factors: list[FactorDefinition]) -> None:
        self.conn.executemany(
            """
            INSERT INTO factors
            (factor_id, activity_type, factor_value, factor_unit, version, effective_from_ms, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(factor_id) DO UPDATE SET
                activity_type=excluded.activity_type, factor_value=excluded.factor_value,
                factor_unit=excluded.factor_unit, version=excluded.version,
                effective_from_ms=excluded.effective_from_ms, source=excluded.source
            """,
            [(f.factor_id, f.activity_type, f.factor_value, f.factor_unit, f.version, f.effective_from_ms, f.source) for f in factors],
        )

    def read_all(self) -> list[FactorDefinition]:
        rows = self.conn.execute("SELECT * FROM factors ORDER BY activity_type, effective_from_ms, version")
        return [FactorDefinition(**dict(row)) for row in rows]
