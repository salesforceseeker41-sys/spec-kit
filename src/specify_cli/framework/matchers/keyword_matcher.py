"""Keyword-based rule matcher."""

from __future__ import annotations

from ...rule_catalog import Rule
from .base import MatchResult


class KeywordMatcher:
    """Simple case-insensitive keyword matcher.

    Sprint 4A intentionally does not implement semantic, regex, or AI matching.
    """

    def match(self, rule: Rule, document_content: str) -> MatchResult:
        normalized_content = document_content.lower()
        matched_keywords: list[str] = []
        missing_keywords: list[str] = []

        for keyword in rule.keywords:
            if keyword.lower() in normalized_content:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        return MatchResult(
            matched=bool(matched_keywords),
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
        )

