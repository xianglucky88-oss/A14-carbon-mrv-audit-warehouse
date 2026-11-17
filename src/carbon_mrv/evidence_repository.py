from __future__ import annotations

from .database import Database
from .models import EvidenceRecord


class EvidenceRepository:
    def __init__(self, database: Database):
        self.conn = database.conn

    def save_many(self, records: list[EvidenceRecord]) -> None:
        self.conn.executemany(
            """
            INSERT INTO evidence
            (evidence_id, facility_id, period_start_ms, period_end_ms, activity_type, value, unit, supplier, evidence_hash, received_at_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(evidence_id) DO UPDATE SET
                facility_id=excluded.facility_id, period_start_ms=excluded.period_start_ms,
                period_end_ms=excluded.period_end_ms, activity_type=excluded.activity_type,
                value=excluded.value, unit=excluded.unit, supplier=excluded.supplier,
                evidence_hash=excluded.evidence_hash, received_at_ms=excluded.received_at_ms
            """,
            [(r.evidence_id, r.facility_id, r.period_start_ms, r.period_end_ms, r.activity_type,
              r.value, r.unit, r.supplier, r.evidence_hash, r.received_at_ms) for r in records],
        )

    def read_all(self) -> list[EvidenceRecord]:
        rows = self.conn.execute("SELECT * FROM evidence ORDER BY facility_id, period_start_ms, evidence_id")
        return [EvidenceRecord(**dict(row)) for row in rows]
