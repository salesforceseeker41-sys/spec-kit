"""Governance finding model for rule-driven advisory reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["info", "advisory", "warning"]


@dataclass(frozen=True)
class GovernanceFinding:
    """One advisory governance finding produced by the Governance Engine."""

    rule_id: str
    rule_title: str
    category: str
    severity: Severity
    artifact: str
    message: str
    recommendation: str
    source_path: str
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    matcher: str = "keyword"
    matcher_version: str = "1.0"
    confidence: float | None = None
    matched_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    negative_evidence_found: list[str] = field(default_factory=list)
    explanation: str = ""

    @property
    def id(self) -> str:
        return self.rule_id

    @property
    def source(self) -> str:
        return self.source_path

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.rule_id,
            "rule_id": self.rule_id,
            "rule_title": self.rule_title,
            "category": self.category,
            "severity": self.severity,
            "artifact": self.artifact,
            "message": self.message,
            "recommendation": self.recommendation,
            "source": self.source_path,
            "source_path": self.source_path,
            "matched_keywords": list(self.matched_keywords),
            "missing_keywords": list(self.missing_keywords),
            "matcher": self.matcher,
            "matcher_version": self.matcher_version,
            "confidence": self.confidence,
            "matched_evidence": list(self.matched_evidence),
            "missing_evidence": list(self.missing_evidence),
            "negative_evidence_found": list(self.negative_evidence_found),
            "explanation": self.explanation,
        }
