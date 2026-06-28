#!/usr/bin/env python3
"""Run advisory Enterprise Governance validation for feature artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()

    from specify_cli.governance_validation import GovernanceValidator

    parser = argparse.ArgumentParser(
        description="Run advisory Enterprise Governance validation."
    )
    parser.add_argument(
        "--feature",
        required=True,
        help="Feature folder or artifact file path.",
    )
    parser.add_argument(
        "--artifact",
        choices=("spec", "specification", "plan", "tasks", "all"),
        default="all",
        help="Artifact to validate. Default: all.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format. Default: text.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write markdown report to governance-review.md in the feature folder.",
    )
    parser.add_argument(
        "--root",
        help="Optional repository root. Defaults to auto-discovery from cwd.",
    )
    parser.add_argument(
        "--matcher",
        choices=("keyword", "practice"),
        help="Optional matcher override. Defaults to enterprise.yaml or keyword.",
    )
    args = parser.parse_args(argv)

    validator = GovernanceValidator(args.root, matcher=args.matcher)
    report = validator.validate(args.feature, artifact=args.artifact)

    if args.format == "json":
        print(report.to_json())
    elif args.format == "markdown":
        print(report.to_markdown(), end="")
    else:
        print(report.to_text(), end="")

    if args.write_report:
        report_path = _report_path(args.feature, validator.root_path)
        existed = report_path.exists()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report.to_markdown(), encoding="utf-8")
        action = "Overwrote existing" if existed else "Wrote"
        print(f"{action} governance report: {report_path}", file=sys.stderr)

    return 1 if report.has_errors() else 0


def _report_path(feature: str, root_path: Path) -> Path:
    path = Path(feature)
    if not path.is_absolute():
        path = root_path / path
    feature_dir = path.parent if path.suffix else path
    return feature_dir / "governance-review.md"


if __name__ == "__main__":
    raise SystemExit(main())
