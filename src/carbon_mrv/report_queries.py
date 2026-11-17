from __future__ import annotations

import json

from .database import Database


class ReportQueries:
    def __init__(self, database: Database):
        self.conn = database.conn

    def summary(self) -> dict[str, object]:
        evidence = self.conn.execute("SELECT COUNT(*) AS n FROM evidence").fetchone()["n"]
        lines = self.conn.execute("SELECT COUNT(*) AS n, COALESCE(SUM(emissions_kgco2e), 0) AS total FROM emission_lines").fetchone()
        restatements = self.conn.execute("SELECT COUNT(*) AS n FROM restatements").fetchone()["n"]
        return {"evidence": evidence, "emission_lines": lines["n"], "total_kgco2e": lines["total"], "restatements": restatements}

    def restatements(self) -> list[dict[str, object]]:
        rows = self.conn.execute("SELECT * FROM restatements ORDER BY facility_id, period_start_ms, created_at_ms")
        result = []
        for row in rows:
            item = dict(row)
            item["changed_evidence_ids"] = json.loads(item["changed_evidence_ids"])
            result.append(item)
        return result
