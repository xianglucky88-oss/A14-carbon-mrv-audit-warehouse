from __future__ import annotations

from .models import CalculationIssue, EvidenceRecord, IngestResult


def _validate(record: EvidenceRecord) -> str | None:
    if not record.evidence_id or not record.facility_id:
        return "evidence_id and facility_id are required"
    if record.period_end_ms <= record.period_start_ms:
        return "period_end_ms must be after period_start_ms"
    if record.value < 0:
        return "activity value must be non-negative"
    if record.activity_type not in {"electricity", "natural_gas", "diesel", "refrigerant"}:
        return f"unsupported activity_type {record.activity_type!r}"
    if not record.unit or not record.supplier or not record.evidence_hash:
        return "unit, supplier and evidence_hash are required"
    return None


def ingest_evidence(records: list[EvidenceRecord], late_grace_ms: int = 86_400_000) -> IngestResult:
    by_id: dict[str, EvidenceRecord] = {}
    issues: list[CalculationIssue] = []
    duplicates = 0
    for record in records:
        problem = _validate(record)
        if problem:
            issues.append(CalculationIssue(record.evidence_id, "evidence_validation", "high", problem))
            continue
        previous = by_id.get(record.evidence_id)
        if previous is not None:
            duplicates += 1
            if record.received_at_ms < previous.received_at_ms:
                continue
        by_id[record.evidence_id] = record
    accepted = sorted(by_id.values(), key=lambda item: (item.facility_id, item.period_start_ms, item.evidence_id))
    late = sum(record.received_at_ms > record.period_end_ms + late_grace_ms for record in accepted)
    return IngestResult(accepted=accepted, issues=issues, duplicates=duplicates, late_records=late)
