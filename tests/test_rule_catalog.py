from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from specify_cli.rule_catalog import RuleLoader


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RULE_FIELDS = {
    "id",
    "title",
    "category",
    "description",
    "rationale",
    "severity",
    "default_enabled",
    "applies_to",
    "keywords",
    "recommendation",
    "references",
    "owner",
    "version",
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_rule(root: Path, category: str = "security", rule_id: str = "SEC-001") -> None:
    _write(
        root / "enterprise" / "rules" / category / f"{rule_id}.yaml",
        f"""
id: {rule_id}
title: CRUD/FLS Enforcement
category: Security
description: All Apex operations must enforce CRUD and FLS.
rationale: Enterprise security policy requires permission enforcement.
severity: advisory
default_enabled: true
applies_to:
  - specification
  - plan
  - apex
keywords:
  - CRUD
  - FLS
recommendation: Explicitly describe CRUD/FLS enforcement.
references:
  - Salesforce Secure Coding Guide
owner: Platform Team
version: "1.0"
future_field: preserved
""".lstrip(),
    )


def test_rule_loader_loads_rules_from_catalog(tmp_path: Path) -> None:
    _write_rule(tmp_path)

    collection = RuleLoader(tmp_path).load()

    assert not collection.has_errors()
    assert collection.list_rule_ids() == ["SEC-001"]
    assert collection.rules[0].owner == "Platform Team"


def test_bundled_rule_catalog_has_unique_ids_and_required_fields() -> None:
    rule_files = sorted((REPO_ROOT / "enterprise" / "rules").glob("*/*.yaml"))
    assert rule_files

    ids: list[str] = []
    for rule_file in rule_files:
        payload = yaml.safe_load(rule_file.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), rule_file.as_posix()
        assert REQUIRED_RULE_FIELDS <= set(payload), rule_file.as_posix()
        ids.append(payload["id"])

    assert len(ids) == len(set(ids))


def test_missing_rule_catalog_folder_warns_without_crashing(tmp_path: Path) -> None:
    collection = RuleLoader(tmp_path).load()

    assert not collection.has_errors()
    assert collection.rules == []
    assert any("Rule catalog folder was not found" in warning for warning in collection.warnings)


def test_malformed_rule_yaml_returns_clear_error(tmp_path: Path) -> None:
    _write(tmp_path / "enterprise/rules/security/BAD-001.yaml", "id: [unterminated\n")

    collection = RuleLoader(tmp_path).load()

    assert collection.has_errors()
    assert any("Rule file is not valid YAML" in error for error in collection.errors)


def test_rule_loader_groups_by_category_and_applies_to(tmp_path: Path) -> None:
    _write_rule(tmp_path)

    collection = RuleLoader(tmp_path).load()

    assert list(collection.by_category()) == ["security"]
    assert "apex" in collection.by_applies_to()
    assert collection.by_applies_to()["apex"][0].id == "SEC-001"


def test_rule_loader_filters_category(tmp_path: Path) -> None:
    _write_rule(tmp_path, category="security", rule_id="SEC-001")
    _write_rule(tmp_path, category="governance", rule_id="GOV-001")

    collection = RuleLoader(tmp_path).load(category="security")

    assert collection.list_rule_ids() == ["SEC-001"]


def test_rule_loader_preserves_unknown_fields_for_schema_evolution(
    tmp_path: Path,
) -> None:
    _write_rule(tmp_path)

    rule = RuleLoader(tmp_path).load().rules[0]

    assert rule.metadata == {"future_field": "preserved"}


def test_load_rules_cli_json_output(tmp_path: Path) -> None:
    _write_rule(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/load-rules.py",
            "--root",
            str(tmp_path),
            "--json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["rule_count"] == 1
    assert payload["rules"][0]["id"] == "SEC-001"


def test_load_rules_cli_yaml_output(tmp_path: Path) -> None:
    _write_rule(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/load-rules.py",
            "--root",
            str(tmp_path),
            "--yaml",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["rules"][0]["id"] == "SEC-001"


def test_load_rules_cli_list_output_filters_category(tmp_path: Path) -> None:
    _write_rule(tmp_path, category="security", rule_id="SEC-001")
    _write_rule(tmp_path, category="governance", rule_id="GOV-001")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/load-rules.py",
            "--root",
            str(tmp_path),
            "--category",
            "governance",
            "--list",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "GOV-001"
