from __future__ import annotations

from .models import EmissionLine, LineageLink


def build_lineage(lines: list[EmissionLine]) -> list[LineageLink]:
    return [
        LineageLink(
            evidence_id=line.evidence_id,
            line_id=line.line_id,
            factor_id=line.factor_id,
            calculation_version=line.calculation_version,
            evidence_hash=line.evidence_hash,
        )
        for line in lines
    ]
