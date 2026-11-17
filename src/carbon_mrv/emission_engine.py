from __future__ import annotations

from dataclasses import dataclass

from .factor_catalog import FactorCatalog
from .models import CalculationIssue, EmissionLine, EvidenceRecord, NormalizedActivity
from .unit_converter import convert_activity


@dataclass(frozen=True, slots=True)
class EngineResult:
    lines: list[EmissionLine]
    issues: list[CalculationIssue]


def calculate_emissions(
    evidence: list[EvidenceRecord],
    factors: FactorCatalog,
    calculation_version: str,
    calculated_at_ms: int,
) -> EngineResult:
    lines: list[EmissionLine] = []
    issues: list[CalculationIssue] = []
    for record in evidence:
        try:
            activity = convert_activity(record.activity_type, record.value, record.unit)
        except ValueError as exc:
            issues.append(CalculationIssue(record.evidence_id, "unit_conversion", "high", str(exc)))
            continue
        factor = factors.resolve(record.activity_type, record.period_end_ms)
        if factor is None:
            issues.append(CalculationIssue(record.evidence_id, "missing_factor", "high", "no effective emission factor"))
            continue
        expected_factor_unit = f"kgCO2e/{activity.unit}"
        if factor.factor_unit != expected_factor_unit:
            issues.append(CalculationIssue(record.evidence_id, "factor_unit_mismatch", "high", f"expected {expected_factor_unit}, got {factor.factor_unit}"))
            continue
        lines.append(EmissionLine(
            line_id=f"line:{record.evidence_id}:{calculation_version}",
            evidence_id=record.evidence_id,
            facility_id=record.facility_id,
            period_start_ms=record.period_start_ms,
            period_end_ms=record.period_end_ms,
            activity_type=record.activity_type,
            activity_value=activity.value,
            activity_unit=activity.unit,
            factor_id=factor.factor_id,
            factor_version=factor.version,
            factor_value=factor.factor_value,
            factor_unit=factor.factor_unit,
            emissions_kgco2e=activity.value * factor.factor_value,
            evidence_hash=record.evidence_hash,
            calculation_version=calculation_version,
            calculated_at_ms=calculated_at_ms,
        ))
    lines.sort(key=lambda item: (item.facility_id, item.period_start_ms, item.evidence_id))
    return EngineResult(lines, issues)
