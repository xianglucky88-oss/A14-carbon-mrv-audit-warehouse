from __future__ import annotations

import argparse

from .demo import run_demo
from .jsonl_io import read_jsonl
from .models import EvidenceRecord, FactorDefinition
from .presentation import print_json
from .report import build_report
from .report_queries import ReportQueries
from .service import CarbonMRVWorkspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="carbon-mrv", description="Carbon MRV audit warehouse")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--db", default=".demo-data/mrv.db")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--evidence")
    ingest.add_argument("--factors")
    ingest.add_argument("--db", required=True)
    calc = sub.add_parser("calculate")
    calc.add_argument("--db", required=True)
    report = sub.add_parser("report")
    report.add_argument("--db", required=True)
    trace = sub.add_parser("trace")
    trace.add_argument("--evidence-id", required=True)
    trace.add_argument("--db", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        print_json(run_demo(args.db))
        return
    if args.command == "ingest":
        with CarbonMRVWorkspace(args.db) as workspace:
            if args.evidence:
                result = workspace.ingest_evidence([EvidenceRecord(**row) for row in read_jsonl(args.evidence)])
                print_json({"accepted": len(result.accepted), "duplicates": result.duplicates, "late_records": result.late_records})
            if args.factors:
                workspace.ingest_factors([FactorDefinition(**row) for row in read_jsonl(args.factors)])
        return
    with CarbonMRVWorkspace(args.db) as workspace:
        if args.command == "calculate":
            result = workspace.calculate()
            print_json({"lines": len(result.lines), "issues": len(result.issues), "restatements": len(result.restatements)})
        elif args.command == "trace":
            print_json(workspace.lineage.trace(args.evidence_id))
        else:
            print_json(build_report(ReportQueries(workspace.database)))


if __name__ == "__main__":
    main()
