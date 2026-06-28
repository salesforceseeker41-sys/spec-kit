# Enterprise Spec Framework Architecture

## Vision

The Enterprise Spec Framework (ESF) extends GitHub Spec Kit for large Salesforce organizations that need consistent architecture, governance, delivery evidence, and product-domain alignment across many applications.

Spec Kit provides the core Spec-Driven Development workflow: describe the feature, plan the implementation, break the plan into tasks, and execute. ESF adds enterprise context and governance around that workflow so specifications and plans are not created in isolation.

ESF solves these recurring enterprise problems:

- Delivery teams repeatedly reinterpret enterprise architecture in feature work.
- Product-specific standards are scattered across documents and team memory.
- Salesforce implementation expectations differ across applications.
- Governance review happens late, after a specification or plan is already expensive to change.
- AI agents depend on prompt interpretation instead of deterministic context and structured rule data.

ESF exists to make governance discoverable, reusable, and eventually automatable while preserving the existing Spec Kit workflow.

## Design Goals

### Enterprise Governance

Platform-owned standards must be visible to every feature workflow. Enterprise architecture, security, compliance, scalability, Salesforce standards, and testing expectations should be expressed once and reused everywhere.

### Product Governance

Product Teams own business-domain standards, integrations, domain models, and events. Product standards complement enterprise standards; they do not replace them.

### Backward Compatibility

Existing Spec Kit commands and generated artifacts must continue to work. ESF features are additive and should degrade gracefully when enterprise governance files are absent.

### Extensibility

The framework must support future rule engines, validators, prompt builders, knowledge packs, product rule packs, CI/CD integrations, and agent-specific adapters without rewriting the foundations.

### Multi-Agent Support

Governance context should be reusable by GitHub Copilot, Claude, Codex, Gemini, and other Spec Kit integrations. Agent-specific prompts should consume common data structures rather than duplicating governance discovery.

### Enterprise Scale

The design targets approximately 50 Salesforce applications, multiple Product Teams, and shared Platform ownership. It must favor convention, deterministic loading, and clear ownership over ad hoc configuration.

### Maintainability

Governance should be expressed as data and documentation wherever possible. Code should load, normalize, render, and eventually evaluate governance data without embedding enterprise policy directly in Python.

## Repository Structure

```text
.
├── enterprise/                 # Platform-owned enterprise governance
│   ├── constitution.md          # Enterprise decision framework
│   ├── principles/              # Architecture, security, compliance, scalability, governance principles
│   ├── salesforce/              # Apex, LWC, Flow, testing, and deployment standards
│   └── rules/                   # Machine-readable enterprise rule catalog
├── products/                    # Product-owned governance packs
│   └── rdra/                    # Sample product standards
├── docs/                        # Human-readable ESF and Spec Kit documentation
├── scripts/                     # CLI helper scripts for context, validation, and catalog inspection
├── src/specify_cli/             # Python package for Spec Kit and ESF loaders/models
├── templates/                   # Spec Kit command and artifact templates
├── tests/                       # Automated tests and smoke checks
├── extensions/                  # Spec Kit extension catalog
├── presets/                     # Spec Kit preset catalog
├── workflows/                   # Spec Kit workflow catalog
├── ARCHITECTURE.md              # Authoritative ESF technical architecture
├── ROADMAP.md                   # Version and sprint roadmap
├── DECISIONS.md                 # Architecture Decision Records
├── CONTRIBUTING.md              # Contribution and governance authoring guidance
└── CHANGELOG.md                 # Release and sprint history
```

Ownership view:

```text
Platform Team
  ├─ enterprise/
  ├─ enterprise.yaml
  ├─ enterprise/rules/
  └─ architecture documentation

Product Teams
  └─ products/<product-id>/

Delivery Teams
  └─ specs/<feature>/
```

## High-Level Architecture

```text
Enterprise Governance
  |
  v
Context Loader
  |
  v
Rule Catalog
  |
  v
Governance Engine
  |
  v
Validator
  |
  v
Prompt Builder (planned)
  |
  v
AI Agent
```

Current implemented flow:

```text
enterprise.yaml + enterprise/ + products/
  |
  v
ContextLoader
  |
  v
ContextBundle

enterprise/rules/**/*.yaml
  |
  v
RuleLoader
  |
  v
RuleCollection / RuleCatalog

specification.md / plan.md / tasks.md
  |
  v
GovernanceEngine
  |
  v
GovernanceReport
```

Sprint 4A connects `ContextBundle` and `RuleCatalog` through a reusable `GovernanceEngine`. Sprint 4B migrates the validator so the Governance Engine is the single execution path for advisory validation.

## Core Components

### EnterpriseConfig

`EnterpriseConfig` is the normalized representation of `enterprise.yaml`. It captures enterprise version, platform name, product name, and context-loading flags.

Responsibilities:

- Represent the machine-readable enterprise configuration.
- Provide defaults for context loading.
- Preserve graceful behavior when `enterprise.yaml` is missing.

### ContextLoader

`ContextLoader` locates the repository root, reads `enterprise.yaml`, resolves the selected product, and loads governance documents in deterministic order.

Responsibilities:

- Discover enterprise, Salesforce, product, and optional feature context.
- Return warnings for missing optional files.
- Return errors for malformed required configuration.
- Avoid prompt-specific formatting.

### ContextBundle

`ContextBundle` is the structured output from `ContextLoader`.

Responsibilities:

- Hold normalized config, loaded documents, warnings, errors, root path, product name, and feature path.
- Render deterministic markdown when needed.
- Provide reusable context to future validators, prompt builders, and agents.

### RuleCatalog

`RuleCatalog` is the facade over a loaded set of enterprise rules.

Responsibilities:

- Group rules by category.
- Group rules by `applies_to`.
- Provide stable access for future rule engines.
- Avoid rule evaluation.

### RuleLoader

`RuleLoader` discovers and loads YAML rule files from `enterprise/rules/`.

Responsibilities:

- Load rules as data.
- Preserve unknown fields for schema evolution.
- Return warnings and errors for missing or malformed catalog files.
- Avoid keyword matching or governance enforcement.

### GovernanceEngine

`GovernanceEngine` evaluates loaded rules against feature artifacts represented in a `ContextBundle`.

Responsibilities:

- Select rules by artifact type and technology.
- Dispatch rules to matchers.
- Produce structured findings.
- Support advisory-first operation with a future path to policy enforcement.
- Record execution statistics.
- Return a structured `GovernanceReport`.

### Validator

The validator is advisory and orchestrates validation without performing rule evaluation itself.

Responsibilities:

- Resolve feature artifacts.
- Load `ContextBundle`.
- Load `RuleCatalog`.
- Create `ExecutionContext`.
- Invoke `GovernanceEngine`.
- Render `GovernanceReport`.
- Never block delivery.

The validator must not perform keyword matching, rule filtering, finding creation, statistics creation, or report construction.

### Prompt Builder (planned)

The planned prompt builder will assemble governance context and rule summaries for agent prompts.

Expected responsibilities:

- Convert `ContextBundle` and selected rules into agent-ready context.
- Preserve command compatibility.
- Avoid embedding enterprise policy directly in templates.

### Knowledge Packs (planned)

Knowledge Packs will package enterprise standards, product standards, rule packs, and supporting prompt context for reuse across repositories.

Expected responsibilities:

- Version governance knowledge independently.
- Enable product-specific packs.
- Support installation and upgrade across many Salesforce applications.

## Component Responsibilities

| Component | Owner | Depends on | Produces | Must not do |
| --- | --- | --- | --- | --- |
| `EnterpriseConfig` | Platform Team | `enterprise.yaml` | normalized config | load files |
| `ContextLoader` | Platform Team | filesystem, `EnterpriseConfig` | `ContextBundle` | validate rules |
| `ContextBundle` | Platform Team | loaded documents | structured context | execute prompts |
| `RuleLoader` | Platform Team | `enterprise/rules/` | `RuleCollection` | evaluate rules |
| `RuleCatalog` | Platform Team | `RuleCollection` | grouped rule access | enforce severity |
| Validator | Platform Team | CLI inputs, loaders, engine | rendered advisory report | evaluate rules |
| GovernanceEngine | Platform Team | context, rules, artifacts | `GovernanceReport` | own rule definitions |
| Prompt Builder | Planned | context, selected rules | prompt context | change command names |

## Public Extension Points

The following APIs are intended as stable extension points for Version 1.0 and future matchers, validators, CI integrations, editor integrations, and agent integrations:

| API | Purpose |
| --- | --- |
| `ContextLoader` | Deterministically loads enterprise, product, and feature context. |
| `ContextBundle` | Structured context passed to engines, prompt builders, and validators. |
| `RuleLoader` | Loads machine-readable rule catalog data. |
| `RuleCatalog` | Groups and exposes loaded rules. |
| `GovernanceEngine` | Evaluates rules against context documents. |
| `ExecutionContext` | Carries context, rules, artifact selection, feature path, and product name into the engine. |
| `ExecutionStatistics` | Reports rule and document execution counts. |
| `RuleMatcher` | Interface for keyword, regex, semantic, AI, or ontology matchers. |
| `GovernanceReport` | Structured report for CLI, CI, editor, and agent integrations. |
| `GovernanceFinding` | One advisory finding linked to a rule. |

Compatibility policy:

- Constructor signatures, documented fields, and `to_dict()` or render helpers should remain backward compatible within the 1.x line.
- Additive fields are allowed when existing callers continue to work.
- Script internals, module-level constants, private helper functions, and test fixtures are not stable APIs.
- Blocking policy, CI behavior, semantic matching, and product rule precedence are future capabilities and are not part of the v1.0 stable API.

## Error Handling and Logging

ESF uses a lightweight exception hierarchy for runtime boundaries:

- `FrameworkError`
- `ConfigurationError`
- `ContextError`
- `RuleCatalogError`
- `ValidationError`
- `EngineError`

CLI scripts continue to control user-facing output. Library modules use Python logging for debug diagnostics and return structured warnings/errors through bundles, collections, and reports.

## Sequence Diagrams

### Current Advisory Review

```text
Developer
  |
  v
Feature artifact
  |
  v
CLI
  |
  v
Validator
  |
  +--> ContextLoader
  |
  +--> RuleLoader
  |
  v
GovernanceEngine
  |
  v
GovernanceReport
```

### Future Integration Review

```text
Developer
  |
  v
Specification / Plan / Tasks
  |
  v
Context Loader
  |
  v
Rule Loader
  |
  v
Governance Engine
  |
  v
GovernanceReport
  |
  v
AI Agent / Report / CI
```

### Planned Prompt Assembly

```text
Agent command
  |
  v
Prompt Builder
  |
  +--> ContextBundle
  |
  +--> RuleCatalog
  |
  v
Agent-specific prompt context
  |
  v
AI Agent
```

## Data Flow

```text
enterprise.yaml
  |
  v
EnterpriseConfig
  |
  v
ContextBundle
  |
  +--> enterprise documents
  +--> Salesforce standards
  +--> product standards
  +--> feature specification

enterprise/rules/**/*.yaml
  |
  v
RuleCollection
  |
  v
Governance Engine
  |
  v
Governance Report
```

The data flow separates discovery from evaluation:

- `ContextLoader` discovers context.
- `RuleLoader` discovers rules.
- `GovernanceEngine` evaluates rules.
- Validators and prompt builders consume outputs.

## Design Principles

### SOLID

Each component has a narrow responsibility. Loaders load, bundles transport data, the engine evaluates, reports render, and validators orchestrate.

### Composition Over Inheritance

ESF favors small composable services such as loaders, catalogs, reports, and renderers over deep inheritance hierarchies.

### Open/Closed Principle

New rule categories, product packs, validators, and prompt builders should be added without modifying stable loader behavior.

### Convention Over Configuration

Standard folders such as `enterprise/`, `products/`, `enterprise/rules/`, and `specs/` reduce configuration burden across many applications.

### Backward Compatibility

Governance features must not break existing Spec Kit projects. Missing ESF files should degrade gracefully where possible.

## Extension Points

### Future Rule Matchers

Rule matchers can evaluate structured rule data against artifacts without changing the catalog schema.

### Semantic Matching

Semantic matchers may compare rule intent to specification and plan content beyond keyword coverage.

### AI-Based Matching

AI-assisted matchers can provide advisory review while preserving deterministic rule selection and report structures.

### CI/CD

CI jobs can run advisory or policy-driven validation using JSON reports.

### VS Code

An editor extension can surface context, rules, and findings inline during specification and planning.

### GitHub App

A GitHub App can comment on pull requests, summarize governance drift, and route exceptions to owners.

## Architectural Decisions

Major decisions are captured in [DECISIONS.md](./DECISIONS.md):

- ADR-001: Layered Governance Model.
- ADR-002: Context Bundle Architecture.
- ADR-003: Rule Catalog and Rule Packs.
- ADR-004: Advisory Validation First.
- ADR-005: Backward Compatibility.

## Future Architecture

Version 2.0 should evolve ESF from documentation and advisory tooling into an enterprise governance platform:

```text
Knowledge Packs
  |
  v
Context Providers
  |
  v
Rule Engine
  |
  +--> Advisory Validation
  +--> CI/CD Integration
  +--> VS Code Extension
  +--> GitHub App
  +--> Governance Dashboard
  |
  v
Enterprise Metrics
```

Expected Version 2.0 capabilities:

- Product-specific and enterprise knowledge packs.
- Rule-driven validation with configurable enforcement policy.
- Multi-agent prompt context generation.
- Governance dashboards and trend metrics.
- CI/CD and pull request integration.
- Exception workflows with ownership and expiration.
