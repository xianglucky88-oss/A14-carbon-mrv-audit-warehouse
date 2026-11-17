from __future__ import annotations

from .database import Database
from .models import LineageLink


class LineageRepository:
    def __init__(self, database: Database):
        self.conn = database.conn

    def replace_all(self, links: list[LineageLink]) -> None:
        self.conn.execute("DELETE FROM lineage")
        self.conn.executemany(
            "INSERT INTO lineage (evidence_id, line_id, factor_id, calculation_version, evidence_hash) VALUES (?, ?, ?, ?, ?)",
            [(l.evidence_id, l.line_id, l.factor_id, l.calculation_version, l.evidence_hash) for l in links],
        )

    def trace(self, evidence_id: str) -> list[dict[str, object]]:
        rows = self.conn.execute(
            """
            SELECT l.evidence_id, l.line_id, l.factor_id, l.calculation_version, l.evidence_hash,
                   e.emissions_kgco2e, e.facility_id, e.period_start_ms, e.period_end_ms
            FROM lineage l LEFT JOIN emission_lines e ON e.line_id = l.line_id
            WHERE l.evidence_id = ? ORDER BY l.line_id
            """,
            (evidence_id,),
        )
        return [dict(row) for row in rows]
