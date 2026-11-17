from __future__ import annotations

from collections import defaultdict

from .models import EmissionLine, Restatement


def detect_restatements(
    previous: list[EmissionLine],
    current: list[EmissionLine],
    tolerance_percent: float = 0.5,
    created_at_ms: int = 0,
) -> list[Restatement]:
    previous_by_period = _aggregate(previous)
    current_by_period = _aggregate(current)
    restatements: list[Restatement] = []
    for key, (current_total, current_ids) in current_by_period.items():
        previous_total, previous_ids = previous_by_period.get(key, (0.0, set()))
        if not previous_ids:
            continue
        delta = current_total - previous_total
        percent = abs(delta) / previous_total * 100 if previous_total else 100.0
        if percent <= tolerance_percent:
            continue
        facility_id, start, end = key
        changed = tuple(sorted(current_ids ^ previous_ids))
        restatements.append(Restatement(
            restatement_id=f"restate:{facility_id}:{start}:{end}:{created_at_ms}",
            facility_id=facility_id,
            period_start_ms=start,
            period_end_ms=end,
            previous_kgco2e=previous_total,
            current_kgco2e=current_total,
            delta_kgco2e=delta,
            delta_percent=percent,
            changed_evidence_ids=changed,
            reason="evidence_or_factor_recalculation",
            created_at_ms=created_at_ms,
        ))
    restatements.sort(key=lambda item: (item.facility_id, item.period_start_ms))
    return restatements


def _aggregate(lines: list[EmissionLine]) -> dict[tuple[str, int, int], tuple[float, set[str]]]:
    grouped: dict[tuple[str, int, int], tuple[float, set[str]]] = defaultdict(lambda: (0.0, set()))
    for line in lines:
        key = (line.facility_id, line.period_start_ms, line.period_end_ms)
        total, ids = grouped[key]
        ids.add(line.evidence_id)
        grouped[key] = (total + line.emissions_kgco2e, ids)
    return dict(grouped)
