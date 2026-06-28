#!/usr/bin/env python3
"""Load the Enterprise Governance context bundle.

This script is intentionally small: all reusable behavior lives in
``specify_cli.enterprise_context`` so future prompts, validators, and agent
integrations can call the same loader.
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

    from specify_cli.enterprise_context import ContextLoader

    parser = argparse.ArgumentParser(
        description="Load deterministic Enterprise Governance context."
    )
    parser.add_argument(
        "--feature",
        help="Optional feature folder or specification file to include.",
    )
    parser.add_argument(
        "--format",
        choices=("list", "markdown", "json"),
        default="list",
        help="Output format. Default: list.",
    )
    parser.add_argument(
        "--root",
        help="Optional repository root. Defaults to auto-discovery from cwd.",
    )
    args = parser.parse_args(argv)

    loader = ContextLoader(args.root)
    bundle = loader.load(feature_path=args.feature)

    if args.format == "markdown":
        print(bundle.render_markdown(), end="")
    elif args.format == "json":
        print(bundle.to_json(include_content=False))
    else:
        for path in bundle.list_loaded_paths():
            print(path)
        if bundle.warnings:
            print("\nWarnings:", file=sys.stderr)
            for warning in bundle.warnings:
                print(f"- {warning}", file=sys.stderr)
        if bundle.errors:
            print("\nErrors:", file=sys.stderr)
            for error in bundle.errors:
                print(f"- {error}", file=sys.stderr)

    return 1 if bundle.has_errors() else 0


if __name__ == "__main__":
    raise SystemExit(main())
