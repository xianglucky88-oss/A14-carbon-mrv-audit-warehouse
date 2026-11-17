from __future__ import annotations

from .models import NormalizedActivity

CANONICAL_UNITS = {
    "electricity": "kWh",
    "natural_gas": "kWh",
    "diesel": "L",
    "refrigerant": "kg",
}


def convert_activity(activity_type: str, value: float, unit: str) -> NormalizedActivity:
    canonical = CANONICAL_UNITS.get(activity_type)
    if canonical is None:
        raise ValueError(f"unsupported activity_type {activity_type!r}")
    if activity_type == "electricity":
        factors = {"Wh": 0.001, "kWh": 1.0, "MWh": 1000.0, "GJ": 277.7777778}
    elif activity_type == "natural_gas":
        factors = {"kWh": 1.0, "MWh": 1000.0, "GJ": 277.7777778, "m3": 10.55}
    elif activity_type == "diesel":
        factors = {"L": 1.0, "gal": 3.785411784, "m3": 1000.0}
    else:
        factors = {"kg": 1.0, "tonne": 1000.0, "t": 1000.0}
    if unit not in factors:
        raise ValueError(f"unsupported unit {unit!r} for {activity_type}")
    return NormalizedActivity(value * factors[unit], canonical)
