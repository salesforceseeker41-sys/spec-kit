#!/usr/bin/env python3
"""Load the Enterprise Rule Catalog.

This script only renders rule data. It does not evaluate, enforce, or validate
feature artifacts against the rules.
"""

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

    from specify_cli.rule_catalog import RuleLoader

    parser = argparse.ArgumentParser(description="Load Enterprise Rule Catalog data.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List loaded rule IDs. This is the default output.",
    )
    parser.add_argument(
        "--category",
        help="Optional Salesforce rule domain to load, such as security, apex, or governance.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Render the loaded rule collection as JSON.",
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Render the loaded rule collection as YAML.",
    )
    parser.add_argument(
        "--root",
        help="Optional repository root. Defaults to auto-discovery from cwd.",
    )
    args = parser.parse_args(argv)

    if args.json and args.yaml:
        parser.error("--json and --yaml are mutually exclusive.")

    loader = RuleLoader(args.root)
    collection = loader.load(category=args.category)

    if args.json:
        print(collection.to_json())
    elif args.yaml:
        print(collection.to_yaml(), end="")
    else:
        for rule_id in collection.list_rule_ids():
            print(rule_id)

    if collection.warnings:
        print("\nWarnings:", file=sys.stderr)
        for warning in collection.warnings:
            print(f"- {warning}", file=sys.stderr)

    if collection.errors:
        print("\nErrors:", file=sys.stderr)
        for error in collection.errors:
            print(f"- {error}", file=sys.stderr)

    return 1 if collection.has_errors() else 0


if __name__ == "__main__":
    raise SystemExit(main())
