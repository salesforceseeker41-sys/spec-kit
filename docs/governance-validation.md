# Advisory Governance Validation

## Purpose

Advisory Governance Validation reviews feature artifacts against the Enterprise Rule Catalog and reports recommendations without blocking delivery.

Sprint 4B refactors validation so the validator is an orchestrator. Governance evaluation now happens through the reusable `GovernanceEngine`.

The validator remains advisory only. It does not block delivery teams, enforce rule severities, approve exceptions, register hooks, invoke AI agents, or run CI gates.

## Validator Architecture

```text
CLI
  |
  v
GovernanceValidator
  |
  +-- ContextLoader -> ContextBundle
  |
  +-- RuleLoader -> RuleCatalog
  |
  v
ExecutionContext
  |
  v
GovernanceEngine
  |
  v
GovernanceReport
```

Responsibilities:

- CLI parses arguments and prints the selected report format.
- `GovernanceValidator` resolves feature artifact paths and wires dependencies.
- `ContextLoader` loads enterprise and product context.
- `RuleLoader` loads rule catalog data.
- `GovernanceEngine` selects applicable rules, invokes matchers, and creates findings.
- `GovernanceReport` renders text, markdown, and JSON.

The validator contains no keyword matching, rule filtering, finding creation, statistics creation, or report construction logic.

## Execution Flow

1. Parse CLI arguments.
2. Resolve the feature folder or artifact file.
3. Load `ContextBundle`.
4. Load `RuleCatalog`.
5. Add available feature artifacts to the context bundle.
6. Create `ExecutionContext`.
7. Invoke `GovernanceEngine`.
8. Render `GovernanceReport`.
9. Exit with non-zero status only for runtime/configuration errors.

Governance findings are advisory and do not cause a failing exit code.

## What Is Checked

The Governance Engine evaluates rules from `enterprise/salesforce/*/rules.yaml`. A rule is applicable when the requested artifact appears in the rule's `applies_to` list.

Current artifact targets:

- `specification`
- `plan`
- `tasks`

The current matcher is `KeywordMatcher`, which checks whether at least one configured rule keyword appears in the artifact content. This is intentionally simple and will be replaced or supplemented by richer matchers in later sprints.

ESF v1.1 adds an opt-in `PracticeComplianceMatcher` for deterministic Salesforce practice evidence. `KeywordMatcher` remains the default.

## What Is Not Checked

Sprint 4B does not implement:

- Blocking validation.
- Severity enforcement.
- Exception approval workflow.
- CI gates.
- Product aliases.
- Multi-product resolution.
- Automatic hook registration.
- AI invocation.
- Semantic matching.

## Artifact Resolution

Given:

```bash
--feature specs/001-provider-program
```

The validator resolves:

- `spec` or `specification`: `specs/001-provider-program/specification.md`
- `plan`: `specs/001-provider-program/plan.md`
- `tasks`: `specs/001-provider-program/tasks.md`
- `all`: all existing artifacts from the list above

Missing requested artifacts produce warnings, not crashes.

## CLI Usage

Validate one artifact:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact spec
python scripts/validate-governance.py --feature specs/001-provider-program --artifact specification
python scripts/validate-governance.py --feature specs/001-provider-program --artifact plan
python scripts/validate-governance.py --feature specs/001-provider-program --artifact tasks
```

Validate all available artifacts:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact all
```

## Output Formats

Text output is the default:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact all --format text
```

Markdown output:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact all --format markdown
```

JSON output for future automation:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact all --format json
```

Opt in to Salesforce Practice Compliance:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact plan --matcher practice
```

If `--matcher` is omitted, the validator uses `enterprise.yaml` when configured and otherwise falls back to `keyword`.

## Report File

Use `--write-report` to write a markdown report to:

```text
specs/<feature>/governance-review.md
```

Example:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --artifact all --write-report
```

If the report already exists, the script overwrites it and clearly states that it did so.

## Limitations

- Default findings are based on rule keyword coverage, not semantic rule evaluation.
- Practice Compliance findings are deterministic evidence checks and remain advisory.
- A mentioned keyword may satisfy a rule even if the design is incomplete.
- A missing keyword may produce a finding even when the artifact addresses the rule indirectly.
- Plan and task documents are added to the execution context by the validator; the Context Loader still loads feature specifications directly.
- Blocking validation and CI policy remain future work.

## Future Roadmap

### Semantic Matching

Future matchers can evaluate rule intent instead of simple keyword presence.

### CI Integration

Future CI integrations should consume `GovernanceReport` JSON without bypassing the Governance Engine.

### Policy and Exceptions

Future policy layers may interpret findings as advisory, warning, or blocking, but that decision should remain outside matchers and rule loading.
