from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    facility_id: str
    period_start_ms: int
    period_end_ms: int
    activity_type: str
    value: float
    unit: str
    supplier: str
    evidence_hash: str
    received_at_ms: int


@dataclass(frozen=True, slots=True)
class NormalizedActivity:
    value: float
    unit: str


@dataclass(frozen=True, slots=True)
class FactorDefinition:
    factor_id: str
    activity_type: str
    factor_value: float
    factor_unit: str
    version: str
    effective_from_ms: int
    source: str


@dataclass(frozen=True, slots=True)
class CalculationIssue:
    evidence_id: str
    rule: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class EmissionLine:
    line_id: str
    evidence_id: str
    facility_id: str
    period_start_ms: int
    period_end_ms: int
    activity_type: str
    activity_value: float
    activity_unit: str
    factor_id: str
    factor_version: str
    factor_value: float
    factor_unit: str
    emissions_kgco2e: float
    evidence_hash: str
    calculation_version: str
    calculated_at_ms: int


@dataclass(frozen=True, slots=True)
class Restatement:
    restatement_id: str
    facility_id: str
    period_start_ms: int
    period_end_ms: int
    previous_kgco2e: float
    current_kgco2e: float
    delta_kgco2e: float
    delta_percent: float
    changed_evidence_ids: tuple[str, ...]
    reason: str
    created_at_ms: int


@dataclass(frozen=True, slots=True)
class LineageLink:
    evidence_id: str
    line_id: str
    factor_id: str
    calculation_version: str
    evidence_hash: str


@dataclass(frozen=True, slots=True)
class IngestResult:
    accepted: list[EvidenceRecord]
    issues: list[CalculationIssue]
    duplicates: int
    late_records: int


@dataclass(frozen=True, slots=True)
class CalculationResult:
    lines: list[EmissionLine]
    issues: list[CalculationIssue]
    restatements: list[Restatement]
    lineage: list[LineageLink]
