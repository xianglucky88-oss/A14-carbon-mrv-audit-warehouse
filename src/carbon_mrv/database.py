from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    period_start_ms INTEGER NOT NULL,
    period_end_ms INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    supplier TEXT NOT NULL,
    evidence_hash TEXT NOT NULL,
    received_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS factors (
    factor_id TEXT PRIMARY KEY,
    activity_type TEXT NOT NULL,
    factor_value REAL NOT NULL,
    factor_unit TEXT NOT NULL,
    version TEXT NOT NULL,
    effective_from_ms INTEGER NOT NULL,
    source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS emission_lines (
    line_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    facility_id TEXT NOT NULL,
    period_start_ms INTEGER NOT NULL,
    period_end_ms INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    activity_value REAL NOT NULL,
    activity_unit TEXT NOT NULL,
    factor_id TEXT NOT NULL,
    factor_version TEXT NOT NULL,
    factor_value REAL NOT NULL,
    factor_unit TEXT NOT NULL,
    emissions_kgco2e REAL NOT NULL,
    evidence_hash TEXT NOT NULL,
    calculation_version TEXT NOT NULL,
    calculated_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS restatements (
    restatement_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    period_start_ms INTEGER NOT NULL,
    period_end_ms INTEGER NOT NULL,
    previous_kgco2e REAL NOT NULL,
    current_kgco2e REAL NOT NULL,
    delta_kgco2e REAL NOT NULL,
    delta_percent REAL NOT NULL,
    changed_evidence_ids TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS lineage (
    evidence_id TEXT NOT NULL,
    line_id TEXT NOT NULL,
    factor_id TEXT NOT NULL,
    calculation_version TEXT NOT NULL,
    evidence_hash TEXT NOT NULL,
    PRIMARY KEY (evidence_id, line_id)
);
"""


class Database:
    def __init__(self, path: str | Path):
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(file_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
