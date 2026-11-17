from __future__ import annotations

import unittest

from carbon_mrv.emission_engine import calculate_emissions
from carbon_mrv.evidence_ingestor import ingest_evidence
from carbon_mrv.factor_catalog import FactorCatalog
from carbon_mrv.models import EmissionLine, EvidenceRecord, FactorDefinition
from carbon_mrv.restatement_detector import detect_restatements
from carbon_mrv.unit_converter import convert_activity


def evidence(value: float, received: int = 2000) -> EvidenceRecord:
    return EvidenceRecord("E1", "F", 1000, 2000, "electricity", value, "MWh", "supplier", "hash", received)


def factor(version: str, value: float, effective: int) -> FactorDefinition:
    return FactorDefinition(f"EF-{version}", "electricity", value, "kgCO2e/kWh", version, effective, "source")


class RuleTests(unittest.TestCase):
    def test_activity_conversion(self) -> None:
        self.assertEqual(convert_activity("electricity", 2, "MWh").value, 2000)
        self.assertAlmostEqual(convert_activity("natural_gas", 1, "m3").value, 10.55)

    def test_latest_effective_factor_is_used(self) -> None:
        catalog = FactorCatalog([factor("v1", 1.0, 100), factor("v2", 2.0, 1500)])
        result = calculate_emissions([evidence(2)], catalog, "calc-v1", 3000)
        self.assertEqual(result.lines[0].factor_version, "v2")
        self.assertEqual(result.lines[0].emissions_kgco2e, 4000)

    def test_evidence_dedup_keeps_latest_received(self) -> None:
        result = ingest_evidence([evidence(1, 2000), evidence(3, 3000)])
        self.assertEqual(result.duplicates, 1)
        self.assertEqual(result.accepted[0].value, 3)

    def test_restatement_detects_material_change(self) -> None:
        old = EmissionLine("l1", "E1", "F", 1000, 2000, "electricity", 1000, "kWh", "EF", "v1", 1, "kgCO2e/kWh", 1000, "h", "v1", 1)
        new = EmissionLine("l2", "E1", "F", 1000, 2000, "electricity", 1200, "kWh", "EF", "v1", 1, "kgCO2e/kWh", 1200, "h", "v1", 2)
        result = detect_restatements([old], [new], tolerance_percent=0.5, created_at_ms=3)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].delta_kgco2e, 200)
