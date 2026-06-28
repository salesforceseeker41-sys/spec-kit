# Governance Engine

## Purpose

The Enterprise Governance Engine is the reusable rule evaluation core for the Enterprise Spec Framework. It evaluates loaded Rule Catalog rules against documents from a `ContextBundle` and returns a structured `GovernanceReport`.

Sprint 4A introduced the engine foundation. Sprint 4B integrates the existing validator with the engine so `GovernanceEngine` is the single execution path for advisory governance validation. The framework still does not add CI integration, blocking validation, semantic matching, or AI evaluation.

## Architecture

```text
Context Loader
  |
  v
ContextBundle
  |
  v
Rule Catalog
  |
  v
Governance Engine
  |
  v
GovernanceReport
```

Package layout:

```text
src/specify_cli/framework/
  engine/
    execution_context.py
    execution_result.py
    execution_statistics.py
    governance_engine.py
  matchers/
    base.py
    evidence_model.py
    keyword_matcher.py
    matcher_resolver.py
    practice_compliance_matcher.py
  reports/
    governance_finding.py
    governance_report.py
```

The engine has no CLI responsibilities. It accepts an `ExecutionContext` and returns an `ExecutionResult` containing a `GovernanceReport`.

## Advisory-Only Behavior

Sprint 4A findings are advisory. Supported severities are:

- `info`
- `advisory`
- `warning`

There is no blocking severity, no policy enforcement, no exception workflow, and no delivery gate.

## Matcher Abstraction

Rule evaluation is delegated to a `RuleMatcher` interface:

```text
RuleMatcher.match(rule, document_content) -> MatchResult
```

`MatchResult` contains:

- `matched`
- `matched_keywords`
- `missing_keywords`
- optional matcher metadata
- optional confidence and practice evidence fields

This allows future matchers to be added without rewriting the engine.

ESF v1.1 adds `PracticeComplianceMatcher` as an opt-in matcher. The engine still receives a matcher instance and does not decide matcher selection:

```text
MatcherResolver -> GovernanceEngine(matcher=selected_matcher)
```

`KeywordMatcher` remains the default.

## Keyword Matcher

`KeywordMatcher` is the default matcher.

Behavior:

- Reads `rule.keywords`.
- Performs case-insensitive substring matching.
- Marks a rule as matched when at least one keyword is present.
- Returns all matched and missing keywords.

The matcher intentionally does not implement semantic matching, regular expression matching, AI evaluation, or practice scoring.

## Practice Compliance Matcher

`PracticeComplianceMatcher` is opt-in in ESF v1.1.

Behavior:

- Reads additive rule fields from the Rule Catalog metadata.
- Evaluates `required_evidence` and `negative_evidence` using deterministic `evidence_terms`.
- Calculates advisory confidence.
- Falls back to keyword evidence for rules without practice evidence.
- Performs no LLM calls, external API calls, telemetry, or blocking decisions.

## Execution Flow

```text
ExecutionContext
  |
  +-- ContextBundle
  +-- RuleCatalog
  +-- artifact
  +-- feature_path
  +-- product_name
  |
  v
GovernanceEngine
  |
  +-- select rules by applies_to
  +-- select document by artifact
  +-- run matcher
  +-- create findings for unmatched rules
  +-- record statistics
  |
  v
GovernanceReport
```

Rule applicability:

- `specification` evaluates rules whose `applies_to` contains `specification`.
- `plan` evaluates rules whose `applies_to` contains `plan`.
- `tasks` evaluates rules whose `applies_to` contains `tasks`.
- `all` evaluates supported artifact types when documents are available.

If the selected artifact document is missing, the engine adds a warning and returns a report without crashing.

Rule catalog loader warnings and errors are carried into the returned report. If a matcher raises an unexpected runtime exception for a rule, the engine records a report error for that rule and continues evaluating the remaining rules.

## Report Model

`GovernanceFinding` contains:

- `rule_id`
- `rule_title`
- `category`
- `severity`
- `artifact`
- `message`
- `recommendation`
- `source_path`
- `matched_keywords`
- `missing_keywords`
- `matcher`
- `matcher_version`
- `confidence`
- `matched_evidence`
- `missing_evidence`
- `negative_evidence_found`
- `explanation`

`GovernanceReport` contains:

- `feature_path`
- `product_name`
- `artifact`
- `findings`
- `warnings`
- `errors`
- `statistics`
- `matcher`
- `matcher_version`

Report helpers:

- `has_findings()`
- `has_errors()`
- `findings_by_category()`
- `to_dict()`
- `to_markdown()`
- `to_text()`

`ExecutionStatistics` records:

- `rules_loaded`
- `rules_evaluated`
- `rules_passed`
- `rules_with_findings`
- `documents_evaluated`
- `execution_time_ms`

## Limitations

- The validator now uses the engine, but still preserves the existing CLI contract.
- The Context Loader currently loads feature specifications directly; plan and task documents can be supplied by future integrations through `ContextBundle` documents.
- Keyword matching is intentionally simple and may produce false positives or false negatives.
- Runtime matcher failures become report errors, not governance findings.
- No semantic, AI, regex, blocking, CI, or exception behavior exists in Sprint 4A.

## Validator Integration

Sprint 4B refactors `scripts/validate-governance.py` and `src/specify_cli/governance_validation.py` to consume `GovernanceEngine` while preserving user-facing CLI compatibility.

Execution path:

1. Load context through `ContextLoader`.
2. Load rules through `RuleLoader`.
3. Build an `ExecutionContext`.
4. Execute `GovernanceEngine`.
5. Render the returned `GovernanceReport`.
6. Preserve advisory behavior by default.

## Future Semantic Matching

Future matchers can implement richer evaluation while keeping the same engine contract:

- Semantic matcher for intent-level coverage.
- AI-assisted matcher for nuanced requirements.
- Structured artifact matcher for known sections.
- Product-specific matcher for domain language.

Each matcher should return `MatchResult` and avoid changing rule catalog ownership.
