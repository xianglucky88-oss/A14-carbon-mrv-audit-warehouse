from __future__ import annotations

from .models import FactorDefinition


class FactorCatalog:
    def __init__(self, definitions: list[FactorDefinition]):
        self.definitions = definitions

    def resolve(self, activity_type: str, at_ms: int) -> FactorDefinition | None:
        candidates = [
            item for item in self.definitions
            if item.activity_type == activity_type and item.effective_from_ms <= at_ms
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: (item.effective_from_ms, item.version))
