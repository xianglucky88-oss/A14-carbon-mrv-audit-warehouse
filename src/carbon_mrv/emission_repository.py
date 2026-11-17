from __future__ import annotations

from .database import Database
from .models import EmissionLine


class EmissionRepository:
    def __init__(self, database: Database):
        self.conn = database.conn

    def read_all(self) -> list[EmissionLine]:
        rows = self.conn.execute("SELECT * FROM emission_lines ORDER BY facility_id, period_start_ms, evidence_id")
        return [EmissionLine(**dict(row)) for row in rows]

    def replace_all(self, lines: list[EmissionLine]) -> None:
        self.conn.execute("DELETE FROM emission_lines")
        self.conn.executemany(
            """
            INSERT INTO emission_lines
            (line_id, evidence_id, facility_id, period_start_ms, period_end_ms, activity_type,
             activity_value, activity_unit, factor_id, factor_version, factor_value, factor_unit,
             emissions_kgco2e, evidence_hash, calculation_version, calculated_at_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(l.line_id, l.evidence_id, l.facility_id, l.period_start_ms, l.period_end_ms,
              l.activity_type, l.activity_value, l.activity_unit, l.factor_id, l.factor_version,
              l.factor_value, l.factor_unit, l.emissions_kgco2e, l.evidence_hash,
              l.calculation_version, l.calculated_at_ms) for l in lines],
        )
