# Architecture Decision Records

This document records major Enterprise Spec Framework architecture decisions. Each ADR captures context, decision, rationale, consequences, and status.

## ADR-001: Layered Governance Model

Status: Accepted

Date: Sprint 1

### Context

Large Salesforce organizations need enterprise-wide standards, product-domain standards, and feature-specific delivery evidence. Without a layered model, delivery teams may redefine architecture in feature artifacts or miss product-specific business rules.

### Decision

ESF uses a three-layer ownership model:

```text
Platform Team
  |
  v
Product Teams
  |
  v
Delivery Teams
```

Platform Team owns enterprise governance. Product Teams own product-domain standards. Delivery Teams own feature requirements and evidence.

### Rationale

This separates enterprise architecture from product semantics and feature delivery. It keeps standards reusable while allowing products to express domain-specific constraints.

### Consequences

Positive:

- Clear ownership.
- Reduced duplicated standards.
- Better alignment across many Salesforce applications.

Tradeoffs:

- Requires governance stewardship.
- Product standards must not conflict silently with enterprise standards.

## ADR-002: Context Bundle Architecture

Status: Accepted

Date: Sprint 2

### Context

Prompt-only instructions such as "read enterprise standards" are not deterministic. Product resolution, missing files, and loading order must be explicit before validators and prompt builders can reuse governance context.

### Decision

ESF introduced `EnterpriseConfig`, `ContextDocument`, `ContextBundle`, and `ContextLoader`.

The loader reads `enterprise.yaml`, resolves `product.name`, loads enterprise and product documents in deterministic order, and returns a structured bundle.

### Rationale

Structured context separates discovery from rendering and makes future prompt builders, validators, and multi-agent integrations depend on the same source of truth.

### Consequences

Positive:

- Deterministic loading.
- Reusable context object.
- Clear warnings for missing optional context.

Tradeoffs:

- `enterprise.yaml` becomes an important repository contract.
- Future product resolution features must preserve deterministic behavior.

## ADR-003: Rule Catalog and Rule Packs

Status: Accepted

Date: Sprint 3.5

### Context

Sprint 3 advisory validation uses hardcoded heuristic governance topics. That is useful for early feedback but not maintainable for enterprise scale.

### Decision

Governance rules are represented as YAML files under `enterprise/salesforce/<domain>/rules.yaml`. The `RuleLoader` loads rules into structured `Rule` objects and returns a `RuleCollection`. Rule loading does not evaluate rules.

### Rationale

Rules should be data. Platform Team can own and version enterprise rules without embedding policy directly in Python.

### Consequences

Positive:

- Rule definitions become auditable.
- Rule schema can evolve.
- Sprint 4 can introduce a rule engine without rewriting rule content.

Tradeoffs:

- Rule quality depends on Platform Team stewardship.
- Schema evolution needs compatibility discipline.

## ADR-004: Advisory Validation First

Status: Accepted

Date: Sprint 3

### Context

Blocking governance too early can slow adoption and create false confidence if rules are incomplete. Delivery teams need feedback before enforcement.

### Decision

Sprint 3 validation is advisory only. Findings are recommendations. Missing artifacts warn without crashing. No blocking severity is introduced.

### Rationale

Advisory mode supports learning, tuning, and trust-building while the rule catalog and engine mature.

### Consequences

Positive:

- Low-friction adoption.
- Useful feedback without stopping delivery.
- Space to refine rules before enforcement.

Tradeoffs:

- Teams can ignore findings.
- Governance impact depends on review discipline until policy enforcement exists.

## ADR-005: Backward Compatibility

Status: Accepted

Date: Sprint 1

### Context

ESF is built on top of GitHub Spec Kit. Existing users and upstream workflows must not be broken by enterprise governance additions.

### Decision

ESF changes are additive. Existing command names, workflow order, scripts, and generated artifacts remain compatible. Governance context is optional and should degrade gracefully when absent.

### Rationale

Backward compatibility allows ESF to be adopted incrementally across many Salesforce applications and reduces merge risk with upstream Spec Kit.

### Consequences

Positive:

- Safer adoption.
- Easier upstream compatibility.
- Lower operational risk.

Tradeoffs:

- Some integrations require additional wrapper scripts instead of deep command changes.
- Governance automation must respect existing Spec Kit behavior.

## ADR-006: Salesforce Practice Compliance Is Opt-In and Local

Status: Accepted

Date: v1.1

### Context

Keyword matching provides useful early advisory feedback, but it cannot reliably distinguish evidence of Salesforce practice compliance from simple term presence. The Platform Team needs deterministic evidence checks for Apex bulkification, Salesforce security, integration reliability, testing, Flow, and LWC practices.

### Decision

ESF v1.1 introduces `PracticeComplianceMatcher` behind the existing `RuleMatcher` abstraction. It is opt-in and local-only. `KeywordMatcher` remains the default. Practice evidence is represented with additive rule fields: `practice`, `required_evidence`, `negative_evidence`, and `evidence_terms`.

### Rationale

This improves Salesforce-specific advisory review without changing existing behavior, introducing LLM risk, or coupling the Governance Engine to matcher selection.

### Consequences

Positive:

- Better Salesforce practice signal than keyword matching alone.
- Deterministic and testable.
- Compatible with future CI/CD and multi-agent integrations.

Tradeoffs:

- Rule authors must maintain evidence terms carefully.
- Confidence remains advisory and can be misunderstood if reports are read as formal approval.
