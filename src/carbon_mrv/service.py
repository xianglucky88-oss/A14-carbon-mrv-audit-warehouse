from __future__ import annotations

import time
from pathlib import Path

from .database import Database
from .emission_engine import calculate_emissions
from .emission_repository import EmissionRepository
from .evidence_ingestor import ingest_evidence
from .evidence_repository import EvidenceRepository
from .factor_catalog import FactorCatalog
from .factor_repository import FactorRepository
from .lineage import build_lineage
from .lineage_repository import LineageRepository
from .models import CalculationResult, EvidenceRecord, FactorDefinition, IngestResult
from .restatement_detector import detect_restatements
from .restatement_repository import RestatementRepository


class CarbonMRVWorkspace:
    def __init__(self, db_path: str | Path):
        self.database = Database(db_path)
        self.evidence = EvidenceRepository(self.database)
        self.factors = FactorRepository(self.database)
        self.emissions = EmissionRepository(self.database)
        self.restatements = RestatementRepository(self.database)
        self.lineage = LineageRepository(self.database)

    def close(self) -> None:
        self.database.close()

    def __enter__(self) -> "CarbonMRVWorkspace":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def ingest_evidence(self, records: list[EvidenceRecord]) -> IngestResult:
        result = ingest_evidence(records)
        self.evidence.save_many(result.accepted)
        self.database.commit()
        return result

    def ingest_factors(self, factors: list[FactorDefinition]) -> None:
        self.factors.save_many(factors)
        self.database.commit()

    def calculate(self, calculation_version: str = "mrv-v1", tolerance_percent: float = 0.5) -> CalculationResult:
        ingested = ingest_evidence(self.evidence.read_all())
        catalog = FactorCatalog(self.factors.read_all())
        calculated_at_ms = int(time.time() * 1000)
        engine = calculate_emissions(ingested.accepted, catalog, calculation_version, calculated_at_ms)
        previous = self.emissions.read_all()
        restatements = detect_restatements(previous, engine.lines, tolerance_percent, calculated_at_ms)
        links = build_lineage(engine.lines)
        self.emissions.replace_all(engine.lines)
        self.lineage.replace_all(links)
        self.restatements.save_many(restatements)
        self.database.commit()
        return CalculationResult(engine.lines, ingested.issues + engine.issues, restatements, links)
