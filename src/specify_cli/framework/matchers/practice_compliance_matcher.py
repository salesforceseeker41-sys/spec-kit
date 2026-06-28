"""Deterministic Salesforce practice compliance matcher."""

from __future__ import annotations

from typing import Any

from ...rule_catalog import Rule
from .base import MatchResult
from .evidence_model import EvidenceResult
from .keyword_matcher import KeywordMatcher


class PracticeComplianceMatcher:
    """Evaluate rule-defined practice evidence without external services.

    The matcher is local, deterministic, and advisory. Existing rules without
    practice evidence fall back to keyword matching.
    """

    name = "practice"
    version = "1.1"

    def __init__(self, *, default_min_confidence: float = 0.7):
        self.default_min_confidence = default_min_confidence
        self.keyword_matcher = KeywordMatcher()

    def match(self, rule: Rule, document_content: str) -> MatchResult:
        required_evidence = _string_list(rule.metadata.get("required_evidence"))
        negative_evidence = _string_list(rule.metadata.get("negative_evidence"))
        evidence_terms = _evidence_terms(rule.metadata.get("evidence_terms"))

        if not required_evidence:
            fallback = self.keyword_matcher.match(rule, document_content)
            return MatchResult(
                matched=fallback.matched,
                matched_keywords=fallback.matched_keywords,
                missing_keywords=fallback.missing_keywords,
                matcher=self.name,
                matcher_version=self.version,
                confidence=1.0 if fallback.matched else 0.0,
                matched_evidence=fallback.matched_keywords,
                missing_evidence=fallback.missing_keywords,
                explanation=(
                    "Rule does not define practice evidence; keyword fallback was used."
                ),
            )

        result = _evaluate_evidence(
            required_evidence=required_evidence,
            negative_evidence=negative_evidence,
            evidence_terms=evidence_terms,
            keywords=rule.keywords,
            document_content=document_content,
        )
        min_confidence = _min_confidence(
            rule.metadata.get("practice"),
            default=self.default_min_confidence,
        )

        return MatchResult(
            matched=result.confidence >= min_confidence,
            matched_keywords=list(result.matched_evidence),
            missing_keywords=list(result.missing_evidence),
            matcher=self.name,
            matcher_version=self.version,
            confidence=result.confidence,
            matched_evidence=result.matched_evidence,
            missing_evidence=result.missing_evidence,
            negative_evidence_found=result.negative_evidence_found,
            explanation=result.explanation,
        )


def _evaluate_evidence(
    *,
    required_evidence: list[str],
    negative_evidence: list[str],
    evidence_terms: dict[str, list[str]],
    keywords: list[str],
    document_content: str,
) -> EvidenceResult:
    normalized_content = _normalize(document_content)
    matched: list[str] = []
    missing: list[str] = []
    negative: list[str] = []

    for evidence in required_evidence:
        terms = evidence_terms.get(evidence, [evidence])
        if _contains_any(normalized_content, terms):
            matched.append(evidence)
        else:
            missing.append(evidence)

    # Existing keywords provide fallback evidence for rules that have practice
    # fields but still carry v1.0 keyword data.
    if not matched and keywords:
        for keyword in keywords:
            if _contains_any(normalized_content, [keyword]):
                matched.append(f"keyword: {keyword}")
                break

    for evidence in negative_evidence:
        terms = evidence_terms.get(evidence, [evidence])
        if _contains_negative_evidence(normalized_content, terms):
            negative.append(evidence)

    total_required = max(len(required_evidence), 1)
    confidence = len([item for item in matched if not item.startswith("keyword: ")])
    if not confidence and any(item.startswith("keyword: ") for item in matched):
        confidence = 1
    confidence = confidence / total_required
    if negative:
        confidence -= min(0.5, 0.15 * len(negative))
    confidence = round(max(0.0, min(1.0, confidence)), 2)

    explanation = _explanation(matched, missing, negative, confidence)
    return EvidenceResult(
        matched_evidence=matched,
        missing_evidence=missing,
        negative_evidence_found=negative,
        confidence=confidence,
        explanation=explanation,
    )


def _contains_any(normalized_content: str, terms: list[str]) -> bool:
    return any(_normalize(term) in normalized_content for term in terms if term)


def _contains_negative_evidence(normalized_content: str, terms: list[str]) -> bool:
    for term in terms:
        normalized_term = _normalize(term)
        if not normalized_term or normalized_term not in normalized_content:
            continue
        negated_forms = (
            f"no {normalized_term}",
            f"avoid {normalized_term}",
            f"avoids {normalized_term}",
            f"without {normalized_term}",
        )
        if any(form in normalized_content for form in negated_forms):
            continue
        return True
    return False


def _normalize(value: str) -> str:
    return " ".join(value.lower().split())


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _evidence_terms(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    terms: dict[str, list[str]] = {}
    for key, raw_terms in value.items():
        label = str(key).strip()
        if not label:
            continue
        if isinstance(raw_terms, list):
            terms[label] = [str(item).strip() for item in raw_terms if str(item).strip()]
        elif raw_terms:
            terms[label] = [str(raw_terms).strip()]
    return terms


def _min_confidence(value: Any, *, default: float) -> float:
    if isinstance(value, dict):
        raw = value.get("min_confidence")
        if isinstance(raw, (int, float)):
            return max(0.0, min(1.0, float(raw)))
    return default


def _explanation(
    matched: list[str], missing: list[str], negative: list[str], confidence: float
) -> str:
    parts = [f"Practice confidence is {confidence:.2f}."]
    if matched:
        parts.append("Matched evidence: " + ", ".join(matched) + ".")
    if missing:
        parts.append("Missing evidence: " + ", ".join(missing) + ".")
    if negative:
        parts.append("Negative evidence found: " + ", ".join(negative) + ".")
    return " ".join(parts)
