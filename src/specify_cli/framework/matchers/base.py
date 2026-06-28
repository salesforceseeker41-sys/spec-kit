"""Matcher interfaces for Governance Engine rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ...rule_catalog import Rule


@dataclass(frozen=True)
class MatchResult:
    matched: bool
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    matcher: str = "keyword"
    matcher_version: str = "1.0"
    confidence: float | None = None
    matched_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    negative_evidence_found: list[str] = field(default_factory=list)
    explanation: str = ""


class RuleMatcher(Protocol):
    def match(self, rule: Rule, document_content: str) -> MatchResult:
        """Return whether *rule* appears addressed by *document_content*."""
