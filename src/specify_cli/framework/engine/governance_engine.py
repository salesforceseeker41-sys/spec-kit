"""Advisory Enterprise Governance Engine core."""

from __future__ import annotations

import logging
import time

from ...enterprise_context import ContextDocument
from ...rule_catalog import Rule
from ..exceptions import EngineError
from ..matchers import KeywordMatcher, RuleMatcher
from ..reports import GovernanceFinding, GovernanceReport
from ..reports.governance_finding import Severity
from .execution_context import ExecutionContext
from .execution_result import ExecutionResult
from .execution_statistics import ExecutionStatistics

SUPPORTED_ARTIFACTS = ("specification", "plan", "tasks")
ARTIFACT_FILES = {
    "specification": "specification.md",
    "plan": "plan.md",
    "tasks": "tasks.md",
}

logger = logging.getLogger(__name__)


class GovernanceEngine:
    """Evaluate rule catalog data against loaded context documents.

    The engine is advisory only. It creates findings when applicable rules are
    not represented by keywords in the relevant artifact document.
    """

    def __init__(self, matcher: RuleMatcher | None = None):
        self.matcher = matcher or KeywordMatcher()

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        started = time.perf_counter()
        warnings = list(context.context_bundle.warnings)
        errors = list(context.context_bundle.errors)
        warnings.extend(context.rule_catalog.collection.warnings)
        errors.extend(context.rule_catalog.collection.errors)
        findings: list[GovernanceFinding] = []
        rules = sorted(context.rule_catalog.rules, key=lambda rule: rule.id)
        artifacts = _artifacts_to_evaluate(context.artifact)
        documents = _documents_by_artifact(context.context_bundle.documents)
        evaluated_rule_ids: set[tuple[str, str]] = set()
        passed_rule_ids: set[tuple[str, str]] = set()
        finding_rule_ids: set[tuple[str, str]] = set()
        evaluated_documents: set[str] = set()

        if not artifacts:
            warnings.append(f"Unsupported artifact for governance engine: {context.artifact}")
        if not rules:
            warnings.append("No governance rules were available for evaluation.")

        for artifact in artifacts:
            document = documents.get(artifact)
            if document is None or not document.exists:
                if context.artifact != "all":
                    warnings.append(f"No document was available for artifact: {artifact}")
                continue

            evaluated_documents.add(document.path)
            applicable_rules = [
                rule for rule in rules if _rule_applies_to(rule, artifact)
            ]
            for rule in applicable_rules:
                key = (artifact, rule.id)
                evaluated_rule_ids.add(key)
                try:
                    result = self.matcher.match(rule, document.content)
                except Exception as exc:  # pragma: no cover - defensive boundary
                    logger.exception(
                        "Rule matcher failed for %s on %s", rule.id, artifact
                    )
                    errors.append(
                        str(
                            EngineError(
                                f"Rule matcher failed for {rule.id} on {artifact}: {exc}"
                            )
                        )
                    )
                    continue
                if result.matched:
                    passed_rule_ids.add(key)
                    continue

                finding_rule_ids.add(key)
                findings.append(
                    GovernanceFinding(
                        rule_id=rule.id,
                        rule_title=rule.title,
                        category=rule.category,
                        severity=_severity(rule.severity),
                        artifact=artifact,
                        message=(
                            f"Rule {rule.id} may not be addressed in "
                            f"{ARTIFACT_FILES[artifact]}."
                        ),
                        recommendation=rule.recommendation,
                        source_path=rule.path,
                        matched_keywords=result.matched_keywords,
                        missing_keywords=result.missing_keywords,
                        matcher=result.matcher,
                        matcher_version=result.matcher_version,
                        confidence=result.confidence,
                        matched_evidence=result.matched_evidence,
                        missing_evidence=result.missing_evidence,
                        negative_evidence_found=result.negative_evidence_found,
                        explanation=result.explanation,
                    )
                )

        statistics = ExecutionStatistics(
            rules_loaded=len(rules),
            rules_evaluated=len(evaluated_rule_ids),
            rules_passed=len(passed_rule_ids),
            rules_with_findings=len(finding_rule_ids),
            documents_evaluated=len(evaluated_documents),
            execution_time_ms=round((time.perf_counter() - started) * 1000),
        )

        report = GovernanceReport(
            feature_path=context.resolved_feature_path(),
            product_name=context.resolved_product_name(),
            artifact=context.artifact,
            findings=findings,
            warnings=warnings,
            errors=errors,
            statistics=statistics,
            matcher=_matcher_name(self.matcher),
            matcher_version=_matcher_version(self.matcher),
        )
        return ExecutionResult(report=report)


def _artifacts_to_evaluate(artifact: str) -> tuple[str, ...]:
    if artifact == "all":
        return SUPPORTED_ARTIFACTS
    if artifact in SUPPORTED_ARTIFACTS:
        return (artifact,)
    return ()


def _documents_by_artifact(
    documents: list[ContextDocument],
) -> dict[str, ContextDocument]:
    mapped: dict[str, ContextDocument] = {}
    for document in documents:
        path = document.path.replace("\\", "/")
        if path.endswith("/specification.md") or path == "specification.md":
            mapped["specification"] = document
        elif path.endswith("/plan.md") or path == "plan.md":
            mapped["plan"] = document
        elif path.endswith("/tasks.md") or path == "tasks.md":
            mapped["tasks"] = document
    return mapped


def _rule_applies_to(rule: Rule, artifact: str) -> bool:
    normalized = {value.lower() for value in rule.applies_to}
    return artifact.lower() in normalized


def _severity(value: str) -> Severity:
    normalized = value.lower()
    if normalized in {"info", "advisory", "warning"}:
        return normalized  # type: ignore[return-value]
    return "advisory"


def _matcher_name(matcher: RuleMatcher) -> str:
    return str(getattr(matcher, "name", "keyword"))


def _matcher_version(matcher: RuleMatcher) -> str:
    return str(getattr(matcher, "version", "1.0"))
