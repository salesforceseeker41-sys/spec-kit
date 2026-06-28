"""Governance report model and renderers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .execution_statistics import ExecutionStatistics
from .governance_finding import GovernanceFinding


@dataclass(frozen=True)
class GovernanceReport:
    """Structured advisory governance report."""

    feature_path: str | None
    product_name: str | None
    artifact: str
    findings: list[GovernanceFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    statistics: ExecutionStatistics = field(default_factory=ExecutionStatistics)

    def has_findings(self) -> bool:
        return bool(self.findings)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def findings_by_category(self) -> dict[str, list[GovernanceFinding]]:
        grouped: dict[str, list[GovernanceFinding]] = {}
        for finding in self.findings:
            grouped.setdefault(finding.category, []).append(finding)
        return {
            category: sorted(findings, key=lambda item: item.rule_id)
            for category, findings in sorted(grouped.items())
        }

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "finding_count": len(self.findings),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "rules_loaded": self.statistics.rules_loaded,
            "rules_evaluated": self.statistics.rules_evaluated,
            "rules_passed": self.statistics.rules_passed,
            "rules_with_findings": self.statistics.rules_with_findings,
            "documents_evaluated": self.statistics.documents_evaluated,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_path": self.feature_path,
            "product_name": self.product_name,
            "artifact": self.artifact,
            "summary": self.summary,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "statistics": self.statistics.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def to_text(self) -> str:
        lines = [
            "Governance Validation Report",
            f"Feature: {self.feature_path or 'none'}",
            f"Product: {self.product_name or 'none'}",
            f"Artifact: {self.artifact}",
            (
                "Summary: "
                f"{len(self.findings)} finding(s), "
                f"{len(self.warnings)} warning(s), "
                f"{len(self.errors)} error(s)"
            ),
            (
                "Statistics: "
                f"{self.statistics.rules_evaluated} rule(s) evaluated, "
                f"{self.statistics.rules_passed} passed, "
                f"{self.statistics.rules_with_findings} with findings"
            ),
        ]
        if self.warnings:
            lines.extend(["", "Warnings:"])
            lines.extend(f"- {warning}" for warning in self.warnings)
        if self.errors:
            lines.extend(["", "Errors:"])
            lines.extend(f"- {error}" for error in self.errors)
        lines.extend(["", "Findings:"])
        if not self.findings:
            lines.append("- No advisory findings.")
        else:
            for finding in self.findings:
                lines.extend(
                    [
                        (
                            f"- {finding.severity.upper()} {finding.rule_id} "
                            f"({finding.category}): {finding.message}"
                        ),
                        f"  Recommendation: {finding.recommendation}",
                    ]
                )
        return "\n".join(lines) + "\n"

    def render_text(self) -> str:
        return self.to_text()

    def to_markdown(self) -> str:
        lines = [
            "# Governance Validation Report",
            "",
            f"- Feature: `{self.feature_path or 'none'}`",
            f"- Product: `{self.product_name or 'none'}`",
            f"- Artifact: `{self.artifact}`",
            f"- Findings: `{len(self.findings)}`",
            f"- Warnings: `{len(self.warnings)}`",
            f"- Errors: `{len(self.errors)}`",
            "",
            "## Statistics",
            "",
            f"- Rules loaded: `{self.statistics.rules_loaded}`",
            f"- Rules evaluated: `{self.statistics.rules_evaluated}`",
            f"- Rules passed: `{self.statistics.rules_passed}`",
            f"- Rules with findings: `{self.statistics.rules_with_findings}`",
            f"- Documents evaluated: `{self.statistics.documents_evaluated}`",
            f"- Execution time: `{self.statistics.execution_time_ms}` ms",
            "",
        ]
        if self.warnings:
            lines.extend(["## Warnings", ""])
            lines.extend(f"- {warning}" for warning in self.warnings)
            lines.append("")
        if self.errors:
            lines.extend(["## Errors", ""])
            lines.extend(f"- {error}" for error in self.errors)
            lines.append("")
        lines.extend(["## Findings", ""])
        if not self.findings:
            lines.extend(["No advisory findings.", ""])
            return "\n".join(lines).rstrip() + "\n"

        for finding in self.findings:
            lines.extend(
                [
                    f"### {finding.rule_id}: {finding.rule_title}",
                    "",
                    f"- Severity: `{finding.severity}`",
                    f"- Category: `{finding.category}`",
                    f"- Artifact: `{finding.artifact}`",
                    f"- Source: `{finding.source_path}`",
                    f"- Message: {finding.message}",
                    f"- Recommendation: {finding.recommendation}",
                    f"- Missing keywords: `{', '.join(finding.missing_keywords)}`",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    def render_markdown(self) -> str:
        return self.to_markdown()
