# Enterprise Spec Framework Roadmap

This roadmap describes the planned evolution of the Enterprise Spec Framework (ESF). Dates are intentionally omitted until release planning is formalized; versions describe capability maturity.

## Version 1.0: Governance Foundation

Version 1.0 establishes the governance scaffold, deterministic context, advisory validation, machine-readable rules, and the core governance engine.

### Version 1.0 Release Candidate

Objective: Package the completed governance foundation for internal enterprise adoption.

Deliverables:

- `VERSION`
- `RELEASE_NOTES_v1.0.md`
- `docs/compatibility.md`
- `docs/release-checklist.md`
- synchronized release documentation
- final compatibility and dependency audit

Acceptance Criteria:

- Existing Spec Kit command behavior remains unchanged.
- ESF validation remains advisory.
- Public extension points are documented.
- Dependency graph remains free of circular imports.
- Release notes, compatibility matrix, and release checklist are available.

Future Work:

- Fresh-clone release verification.
- Platform Team rule wording approval.
- Git tag `v1.0.0` after final maintainer approval.

### Sprint 1: Enterprise and Product Governance

Objective: Create the governance scaffold for enterprise and product standards.

Deliverables:

- `enterprise/`
- `enterprise/constitution.md`
- `enterprise/principles/`
- `enterprise/salesforce/`
- `products/`
- sample `products/rdra/`
- `enterprise.yaml`
- governance documentation
- additive prompt guidance for `/speckit.specify`, `/speckit.plan`, and `/speckit.tasks`

Dependencies:

- Existing Spec Kit template and command structure.

Acceptance Criteria:

- Enterprise standards have a clear home.
- Product standards have a clear home.
- Delivery teams receive prompt guidance without workflow changes.

Future Work:

- Deterministic loading.
- Rule-based validation.
- Product-specific rule packs.

### Sprint 2: Enterprise Context Loader

Objective: Make governance context discoverable, ordered, and reusable.

Deliverables:

- `EnterpriseConfig`
- `ContextDocument`
- `ContextBundle`
- `ContextLoader`
- `scripts/load-enterprise-context.py`
- `docs/context-loader.md`
- context loader tests

Dependencies:

- Sprint 1 folder structure.
- `enterprise.yaml`.

Acceptance Criteria:

- Missing `enterprise.yaml` warns without crashing.
- Product is resolved from `product.name`.
- Enterprise, Salesforce, product, and optional feature context load deterministically.
- Markdown, JSON, and list outputs are available.

Future Work:

- Use `ContextBundle` in prompt builders.
- Use `ContextBundle` in rule-driven validation.

### Sprint 3: Advisory Governance Validation

Objective: Provide non-blocking governance feedback for feature artifacts.

Deliverables:

- `GovernanceFinding`
- `GovernanceValidationReport`
- advisory validator
- `scripts/validate-governance.py`
- `docs/governance-validation.md`
- optional `governance-review.md` output
- validation tests

Dependencies:

- Sprint 2 Context Loader.

Acceptance Criteria:

- Validates `specification.md`, `plan.md`, `tasks.md`, or all available artifacts.
- Supports text, markdown, and JSON.
- Missing artifacts warn without crashing.
- Findings are advisory only.

Future Work:

- Replace hardcoded heuristics with rule-driven evaluation. Completed in Sprint 4B.
- Add structured rule matchers.

### Sprint 3.5: Enterprise Rule Catalog

Objective: Represent governance rules as machine-readable data.

Deliverables:

- `enterprise/rules/`
- YAML rule schema
- sample enterprise rule catalog
- `Rule`
- `RuleCategory`
- `RuleCollection`
- `RuleCatalog`
- `RuleLoader`
- `scripts/load-rules.py`
- `docs/rule-catalog.md`
- rule catalog tests

Dependencies:

- Sprint 1 governance categories.
- Sprint 3 advisory validation concepts.

Acceptance Criteria:

- Rules are data.
- Rule IDs are unique.
- Required fields are documented.
- Loader supports list, category, JSON, and YAML outputs.
- No validation behavior changes.

Future Work:

- Rule engine.
- Product rule packs.
- Rule versioning workflows.

### Sprint 4A: Governance Engine Core

Objective: Create the reusable Governance Engine foundation that evaluates rule catalog data against feature artifacts while preserving advisory-only behavior.

Deliverables:

- `GovernanceEngine`
- `ExecutionContext`
- `ExecutionStatistics`
- `GovernanceReport`
- `GovernanceFinding`
- rule selection by `applies_to`
- matcher interface and `KeywordMatcher`
- initial keyword matcher using rule data
- structured findings mapped from rules

Dependencies:

- Sprint 2 Context Loader.
- Sprint 3.5 Rule Catalog.

Acceptance Criteria:

- Validator behavior remains advisory by default.
- Rules come from YAML, not embedded Python policy.
- Reports identify rule IDs and source rule files.
- Existing CLI behavior is unchanged.

Future Work:

- Validator migration from hardcoded Sprint 3 heuristics. Completed in Sprint 4B.
- Semantic matching.
- AI-assisted matching.
- Enforcement policy.

### Sprint 4B: Validator Engine Integration

Objective: Make the Governance Engine the single execution path for advisory validation while preserving CLI compatibility.

Deliverables:

- Refactored `GovernanceValidator` orchestration.
- `validate-governance.py` rendering through `GovernanceReport`.
- `spec` and `specification` artifact support.
- Removal of hardcoded heuristic evaluation from the validator.
- Regression tests proving engine invocation and CLI compatibility.

Dependencies:

- Sprint 4A Governance Engine Core.
- Sprint 3.5 Rule Catalog.
- Sprint 2 Context Loader.

Acceptance Criteria:

- Validator contains no governance evaluation logic.
- Governance Engine performs rule filtering, matching, finding creation, statistics, and report creation.
- Existing CLI options continue working.
- Text, markdown, JSON, and report writing continue working.

Future Work:

- Semantic matching.
- AI-assisted matching.
- CI integration.
- Policy and exception workflow.

### Sprint 4.5: Architecture Hardening

Objective: Prepare the Enterprise Spec Framework for long-term maintenance and v1.0 release readiness without changing user-facing behavior.

Deliverables:

- Dependency direction review.
- Circular import architecture test.
- ESF exception hierarchy.
- Library logging at defensive boundaries.
- `ExecutionStatistics` dependency cleanup.
- Public extension point documentation.
- `docs/architecture-review.md`.

Dependencies:

- Sprint 4A Governance Engine Core.
- Sprint 4B Validator Engine Integration.

Acceptance Criteria:

- No CLI behavior changes.
- No governance behavior changes.
- No circular dependencies.
- Reports remain independent of CLI and engine internals.
- Documentation reflects actual implementation.

Future Work:

- Rule schema validation.
- Artifact constant consolidation.
- Dedicated report renderer abstraction if additional formats are added.

## Version 1.1: Operationalization

Version 1.1 moves ESF from foundation to adoption across product teams.

### Sprint 5: Product Rule Packs

Objective: Allow Product Teams to add product-specific rule packs.

Deliverables:

- product rule pack structure
- rule precedence model
- product ownership guidance
- conflict reporting

Dependencies:

- Sprint 4A Governance Engine Core.
- Sprint 4B Validator Engine Integration.
- Product governance folders.

Acceptance Criteria:

- Product rules can extend enterprise rules.
- Delivery teams cannot override enterprise rules accidentally.
- Rule provenance is visible in reports.

Future Work:

- Pack versioning.
- Product rule catalog publishing.

### Sprint 6: Context Providers and Prompt Builder

Objective: Build reusable prompt context assembly for multiple agents.

Deliverables:

- context provider interface
- prompt builder
- agent-neutral governance context format
- prompt integration guidance

Dependencies:

- ContextBundle.
- RuleCatalog.
- Spec Kit integration model.

Acceptance Criteria:

- Prompt templates can consume generated context where available.
- Governance context remains ordered and deterministic.
- Agent-specific behavior remains isolated.

Future Work:

- Multi-agent adapters.
- Token-aware context compression.

### Sprint 7: Advisory CI Integration

Objective: Make governance review available in CI without blocking by default.

Deliverables:

- CI-friendly JSON reports
- sample GitHub Actions workflow
- advisory pull request summary format
- artifact upload guidance

Dependencies:

- Sprint 4A Governance Engine Core.
- Sprint 4B Validator Engine Integration.
- Stable report format.

Acceptance Criteria:

- CI can run governance validation.
- Findings remain advisory unless policy enables blocking.
- Output is deterministic and machine-readable.

Future Work:

- Blocking policy.
- Exception workflow.

### Sprint 8: Exception and Policy Model

Objective: Introduce controlled policy enforcement and exception handling.

Deliverables:

- severity policy model
- exception metadata
- owner and expiry fields
- advisory, warning, and blocking modes

Dependencies:

- Rule Engine.
- CI integration.
- Governance ownership model.

Acceptance Criteria:

- Blocking is opt-in.
- Exceptions are explicit, owned, and reviewable.
- Reports distinguish findings from policy decisions.

Future Work:

- Enterprise dashboards.
- Approval workflows.

## Version 2.0: Enterprise Governance Platform

### Knowledge Packs

Objective: Package enterprise and product governance for reuse across repositories.

Deliverables:

- installable governance packs
- versioned rule and context bundles
- upgrade guidance

Acceptance Criteria:

- New applications can adopt ESF consistently.
- Platform Team can publish updates across teams.

### Governance Dashboard

Objective: Provide portfolio-level visibility into governance adoption and risk.

Deliverables:

- report aggregation model
- trend metrics
- product-level dashboards

Acceptance Criteria:

- Platform and Product Teams can see recurring gaps.
- Metrics support improvement without punishing delivery teams.

### CI Integration

Objective: Mature advisory CI into configurable enforcement.

Deliverables:

- reusable workflows
- policy modes
- exception support

Acceptance Criteria:

- Teams can choose advisory or blocking policy by environment.
- Reports remain transparent and auditable.

### VS Code Extension

Objective: Bring ESF context and rule findings into the editor.

Deliverables:

- rule browser
- inline governance findings
- context preview

Acceptance Criteria:

- Developers can see governance feedback before committing.

### GitHub App

Objective: Provide pull request review, comments, and exception routing.

Deliverables:

- PR summary comments
- reviewer routing
- exception workflows

Acceptance Criteria:

- Governance feedback appears where delivery teams already work.

### Enterprise Metrics

Objective: Track governance coverage, rule adoption, exception aging, and product risk.

Deliverables:

- metric definitions
- report ingestion
- product and enterprise views

Acceptance Criteria:

- Metrics are actionable, explainable, and tied to improvement plans.
