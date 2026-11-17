from __future__ import annotations

from .report_queries import ReportQueries


def build_report(queries: ReportQueries) -> dict[str, object]:
    return {"summary": queries.summary(), "restatements": queries.restatements()}
