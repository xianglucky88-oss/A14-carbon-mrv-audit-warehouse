from __future__ import annotations

from pathlib import Path

from .models import EvidenceRecord, FactorDefinition
from .service import CarbonMRVWorkspace


def _evidence(value: float, received_at_ms: int) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="EV-ELEC-001",
        facility_id="FAC-01",
        period_start_ms=1_767_225_600_000,
        period_end_ms=1_767_484_800_000,
        activity_type="electricity",
        value=value,
        unit="MWh",
        supplier="utility-a",
        evidence_hash="sha256:demo-electricity",
        received_at_ms=received_at_ms,
    )


def _factors() -> list[FactorDefinition]:
    return [
        FactorDefinition("EF-ELEC-CN-2025", "electricity", 0.5703, "kgCO2e/kWh", "2025.1", 1_735_689_600_000, "demo-grid-factor"),
        FactorDefinition("EF-GAS-2025", "natural_gas", 0.1810, "kgCO2e/kWh", "2025.1", 1_735_689_600_000, "demo-gas-factor"),
    ]


def run_demo(db_path: str | Path) -> dict[str, object]:
    path = Path(db_path)
    if path.exists():
        path.unlink()
    with CarbonMRVWorkspace(path) as workspace:
        workspace.ingest_factors(_factors())
        workspace.ingest_evidence([_evidence(100.0, 1_767_490_000_000)])
        first = workspace.calculate("mrv-v1")
        workspace.ingest_evidence([_evidence(120.0, 1_767_500_000_000)])
        second = workspace.calculate("mrv-v1")
        return {
            "first_lines": len(first.lines),
            "first_total_kgco2e": sum(line.emissions_kgco2e for line in first.lines),
            "restatements": len(second.restatements),
            "restatement_delta_kgco2e": second.restatements[0].delta_kgco2e if second.restatements else 0,
            "lineage_links": len(second.lineage),
        }
