from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from specify_cli.framework.engine import ExecutionResult
from specify_cli.framework.matchers import KeywordMatcher, MatcherResolver, PracticeComplianceMatcher
from specify_cli.framework.reports import GovernanceReport
from specify_cli.governance_validation import GovernanceValidator


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_config(root: Path, product_name: str = "rdra") -> None:
    _write(
        root / "enterprise.yaml",
        f"""
schema_version: "1.0"
enterprise:
  version: "1.0"
platform:
  name: "Enterprise Platform"
product:
  name: "{product_name}"
context:
  loadEnterprise: true
  loadProduct: true
""".lstrip(),
    )


def _write_minimum_context(root: Path) -> None:
    _write_config(root)
    _write(root / "enterprise/constitution.md", "# Constitution\n")
    _write(root / "enterprise/principles/security.md", "# Security\n")
    _write(root / "enterprise/salesforce/testing.md", "# Testing\n")
    _write(root / "products/rdra/principles.md", "# RDRA Principles\n")
    _write(
        root / "enterprise/salesforce/security/rules.yaml",
        """
rules:
  - id: SEC-COVERAGE
    title: CRUD/FLS Enforcement
    category: security
    description: Security coverage must describe CRUD/FLS enforcement.
    rationale: Enterprise security policy requires explicit permission enforcement.
    severity: advisory
    default_enabled: true
    applies_to:
      - specification
      - plan
      - tasks
    keywords:
      - CRUD/FLS
      - CRUD
      - FLS
    recommendation: Add explicit security coverage for CRUD/FLS and sharing.
    references:
      - Salesforce Secure Coding Guide
    owner: Platform Team
    version: "1.0"
""".lstrip(),
    )


def _write_practice_rule(root: Path) -> None:
    _write(
        root / "enterprise/salesforce/apex/rules.yaml",
        """
rules:
  - id: APEX-PRACTICE
    title: Apex Bulkification
    category: Apex
    description: Apex plans must show bulk-safe design evidence.
    rationale: Bulk-safe design protects governor limits.
    severity: advisory
    default_enabled: true
    applies_to:
      - plan
    keywords:
      - bulkification
    recommendation: Add explicit bulkification evidence.
    references:
      - Salesforce Apex Best Practices
    owner: Platform Team
    version: "1.1"
    practice:
      type: salesforce_apex_bulkification
      min_confidence: 0.7
    required_evidence:
      - processes records in collections
      - avoids SOQL inside loops
      - avoids DML inside loops
    negative_evidence:
      - DML inside loop
    evidence_terms:
      processes records in collections:
        - collections
      avoids SOQL inside loops:
        - query outside loop
      avoids DML inside loops:
        - DML outside loop
      DML inside loop:
        - DML inside loop
""".lstrip(),
    )


def test_matcher_resolver_selects_keyword_by_default(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)

    matcher = MatcherResolver(tmp_path).resolve()

    assert isinstance(matcher, KeywordMatcher)


def test_matcher_resolver_selects_practice_from_enterprise_yaml(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    config = (tmp_path / "enterprise.yaml").read_text(encoding="utf-8")
    (tmp_path / "enterprise.yaml").write_text(
        config + "\ngovernance:\n  matcher: practice\n",
        encoding="utf-8",
    )

    matcher = MatcherResolver(tmp_path).resolve()

    assert isinstance(matcher, PracticeComplianceMatcher)


def test_matcher_resolver_cli_override_wins_over_config(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    config = (tmp_path / "enterprise.yaml").read_text(encoding="utf-8")
    (tmp_path / "enterprise.yaml").write_text(
        config + "\ngovernance:\n  matcher: practice\n",
        encoding="utf-8",
    )

    matcher = MatcherResolver(tmp_path).resolve("keyword")

    assert isinstance(matcher, KeywordMatcher)


def test_invalid_matcher_config_returns_clear_report_error(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    config = (tmp_path / "enterprise.yaml").read_text(encoding="utf-8")
    (tmp_path / "enterprise.yaml").write_text(
        config + "\ngovernance:\n  matcher: unsupported\n",
        encoding="utf-8",
    )
    _write(tmp_path / "specs/001-provider-program/plan.md", "# Plan\n")

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-provider-program", artifact="plan"
    )

    assert report.has_errors()
    assert "Unsupported governance matcher 'unsupported'" in report.errors[0]


def test_missing_feature_folder_produces_warning(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-missing-feature", artifact="all"
    )

    assert not report.has_errors()
    assert any("Feature folder was not found" in warning for warning in report.warnings)
    assert any("No governance artifacts were found" in warning for warning in report.warnings)


def test_missing_requested_artifact_warns_without_crashing(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    (tmp_path / "specs/001-provider-program").mkdir(parents=True)

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-provider-program", artifact="spec"
    )

    assert not report.has_errors()
    assert any("Artifact 'spec' was not found" in warning for warning in report.warnings)


def test_specification_without_security_language_gets_advisory_finding(
    tmp_path: Path,
) -> None:
    _write_minimum_context(tmp_path)
    _write(
        tmp_path / "specs/001-provider-program/specification.md",
        "# Specification\n\nUsers can submit provider program requests.\n",
    )

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-provider-program", artifact="spec"
    )

    assert any(finding.id == "SEC-COVERAGE" for finding in report.findings)
    assert all(finding.severity == "advisory" for finding in report.findings)


def test_plan_mentioning_crud_fls_reduces_security_finding(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(
        tmp_path / "specs/001-provider-program/plan.md",
        "# Plan\n\nSecurity design covers CRUD/FLS and the sharing model.\n",
    )

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-provider-program", artifact="plan"
    )

    assert not any(finding.id == "SEC-COVERAGE" for finding in report.findings)


def test_artifact_all_validates_available_artifacts(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")
    _write(tmp_path / "specs/001-provider-program/tasks.md", "# Tasks\n")

    report = GovernanceValidator(tmp_path).validate(
        "specs/001-provider-program", artifact="all"
    )

    assert report.summary["documents_evaluated"] == 2
    assert {finding.artifact for finding in report.findings} == {
        "specification",
        "tasks",
    }


def test_format_json_returns_parseable_json(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate-governance.py",
            "--root",
            str(tmp_path),
            "--feature",
            "specs/001-provider-program",
            "--artifact",
            "spec",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["artifact"] == "spec"
    assert payload["summary"]["finding_count"] >= 1
    assert payload["findings"][0]["rule_id"] == "SEC-COVERAGE"


def test_cli_accepts_specification_artifact_alias(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate-governance.py",
            "--root",
            str(tmp_path),
            "--feature",
            "specs/001-provider-program",
            "--artifact",
            "specification",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["artifact"] == "specification"


def test_write_report_creates_governance_review_md(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate-governance.py",
            "--root",
            str(tmp_path),
            "--feature",
            "specs/001-provider-program",
            "--artifact",
            "spec",
            "--write-report",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    report_path = tmp_path / "specs/001-provider-program/governance-review.md"
    assert result.returncode == 0
    assert report_path.is_file()
    assert "# Governance Validation Report" in report_path.read_text(encoding="utf-8")
    assert "Wrote governance report" in result.stderr


def test_json_output_stays_parseable_when_writing_report(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate-governance.py",
            "--root",
            str(tmp_path),
            "--feature",
            "specs/001-provider-program",
            "--artifact",
            "spec",
            "--format",
            "json",
            "--write-report",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["artifact"] == "spec"
    assert "governance report" in result.stderr


def test_cli_practice_matcher_outputs_matcher_metadata(tmp_path: Path) -> None:
    _write_minimum_context(tmp_path)
    _write_practice_rule(tmp_path)
    _write(
        tmp_path / "specs/001-provider-program/plan.md",
        "# Plan\n\nThe Apex service processes records in collections but uses DML inside loop.\n",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate-governance.py",
            "--root",
            str(tmp_path),
            "--feature",
            "specs/001-provider-program",
            "--artifact",
            "plan",
            "--matcher",
            "practice",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["matcher"] == {"name": "practice", "version": "1.1"}
    practice_finding = next(
        finding for finding in payload["findings"] if finding["rule_id"] == "APEX-PRACTICE"
    )
    assert practice_finding["matcher"] == "practice"
    assert practice_finding["confidence"] == 0.18
    assert practice_finding["matched_evidence"] == [
        "processes records in collections"
    ]
    assert practice_finding["negative_evidence_found"] == ["DML inside loop"]


def test_validator_invokes_governance_engine(tmp_path: Path) -> None:
    class RecordingEngine:
        def __init__(self) -> None:
            self.called = False

        def execute(self, context):  # noqa: ANN001
            self.called = True
            return ExecutionResult(
                report=GovernanceReport(
                    feature_path=context.feature_path,
                    product_name=context.product_name,
                    artifact=context.artifact,
                )
            )

    _write_minimum_context(tmp_path)
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Spec\n")
    engine = RecordingEngine()

    GovernanceValidator(tmp_path, engine=engine).validate(
        "specs/001-provider-program", artifact="spec"
    )

    assert engine.called


def test_validator_no_longer_contains_heuristic_coverage_checks() -> None:
    source = (REPO_ROOT / "src/specify_cli/governance_validation.py").read_text(
        encoding="utf-8"
    )

    assert "COVERAGE_CHECKS" not in source
    assert "CoverageCheck" not in source
    assert "normalized = content.lower()" not in source
