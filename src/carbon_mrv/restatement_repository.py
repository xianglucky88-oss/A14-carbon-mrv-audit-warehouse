from __future__ import annotations

import json

from .database import Database
from .models import Restatement


class RestatementRepository:
    def __init__(self, database: Database):
        self.conn = database.conn

    def save_many(self, rows: list[Restatement]) -> None:
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO restatements
            (restatement_id, facility_id, period_start_ms, period_end_ms, previous_kgco2e,
             current_kgco2e, delta_kgco2e, delta_percent, changed_evidence_ids, reason, created_at_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(r.restatement_id, r.facility_id, r.period_start_ms, r.period_end_ms, r.previous_kgco2e,
              r.current_kgco2e, r.delta_kgco2e, r.delta_percent, json.dumps(r.changed_evidence_ids),
              r.reason, r.created_at_ms) for r in rows],
        )
