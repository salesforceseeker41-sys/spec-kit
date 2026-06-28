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


class RuleMatcher(Protocol):
    def match(self, rule: Rule, document_content: str) -> MatchResult:
        """Return whether *rule* appears addressed by *document_content*."""

