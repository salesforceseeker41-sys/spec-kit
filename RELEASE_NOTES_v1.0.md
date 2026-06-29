# Enterprise Spec Framework v1.0 Release Notes

## Vision

Enterprise Spec Framework (ESF) extends GitHub Spec Kit with deterministic enterprise governance for large Salesforce organizations. Version 1.0 establishes the foundation for Platform Teams, Product Teams, Delivery Teams, AI coding agents, and future CI/CD integrations to use the same governance context, rules, and advisory reports.

The v1.0 release is intentionally advisory. It helps teams discover governance gaps early without blocking delivery.

## Major Features

### Enterprise Governance Scaffold

- Platform-owned governance under `enterprise/`.
- Salesforce standards under `enterprise/salesforce/`.
- Product-owned standards under `products/<product-id>/`.
- Sample RDRA product documentation.
- Enterprise configuration through `enterprise.yaml`.
- Additive prompt guidance for `/speckit.specify`, `/speckit.plan`, and `/speckit.tasks`.

### Deterministic Context Loader

- `EnterpriseConfig`, `ContextDocument`, `ContextBundle`, and `ContextLoader`.
- Product resolution from `enterprise.yaml` using `product.name`.
- Deterministic loading order for enterprise, Salesforce, product, and feature context.
- List, markdown, and JSON output through `scripts/load-enterprise-context.py`.
- Graceful warnings for missing optional governance files.

### Enterprise Rule Catalog

- Machine-readable YAML rules under `enterprise/salesforce/<domain>/rules.yaml`.
- Rule categories for security, governance, scalability, compliance, architecture, Apex, LWC, Flow, and testing.
- Rule loading through `RuleLoader`, `RuleCollection`, and `RuleCatalog`.
- Rule inspection through `scripts/load-rules.py`.
- Rule schema documentation for Platform Team ownership and future evolution.

### Governance Engine

- Reusable `GovernanceEngine` for advisory rule evaluation.
- `ExecutionContext`, `ExecutionStatistics`, `GovernanceReport`, and `GovernanceFinding`.
- Replaceable `RuleMatcher` abstraction with `KeywordMatcher`.
- Structured report output for CLI, future CI, editor integrations, and AI agents.
- Advisory-only severity model for v1.0.

### Advisory Validator

- `scripts/validate-governance.py` validates `specification.md`, `plan.md`, `tasks.md`, or all available artifacts.
- Supports text, markdown, and JSON output.
- Optional `governance-review.md` report writing.
- Missing artifacts warn instead of crashing.
- The validator uses the Governance Engine as the single evaluation path.

## Architecture

The implemented v1.0 architecture is:

```text
CLI / scripts
  |
  v
GovernanceValidator
  |
  +--> ContextLoader
  +--> RuleLoader
  |
  v
ExecutionContext
  |
  v
GovernanceEngine
  |
  +--> RuleMatcher
  +--> RuleCatalog
  +--> ContextBundle
  |
  v
GovernanceReport
```

Public extension points are documented in `ARCHITECTURE.md` and `docs/architecture-review.md`.

## Supported Capabilities

- Spec Kit workflow compatibility.
- Enterprise and product governance documentation.
- Deterministic governance context loading.
- Enterprise rule catalog loading.
- Advisory validation for specifications, plans, and tasks.
- Rule-driven keyword matching.
- Stable structured reports.
- JSON output for future automation.
- Markdown output for human review.
- Internal architecture tests for ESF dependency boundaries.

## Known Limitations

- Validation is advisory only.
- No blocking governance policy is included.
- No semantic, AI, ontology, or regex matcher is included.
- No product-specific rule pack precedence model is included.
- No CI/CD integration or GitHub Actions workflow is included.
- No exception approval workflow is included.
- No telemetry, metrics, dashboard, or central report aggregation is included.
- Rule schema validation is intentionally lightweight.
- Some upstream Spec Kit tests require Windows symlink privileges or agent-specific home-directory isolation; ESF v1.0 does not require those privileges for normal governance loading or validation.

## Migration Notes

Existing Spec Kit users can adopt ESF incrementally:

1. Keep existing Spec Kit commands and workflow.
2. Add or customize `enterprise/`, `products/`, and `enterprise.yaml`.
3. Run `python scripts/load-enterprise-context.py` to inspect loaded context.
4. Run `python scripts/load-rules.py --list` to inspect enterprise rules.
5. Run `python scripts/validate-governance.py --feature specs/<feature> --artifact all` for advisory review.

No existing Spec Kit command names are changed by ESF v1.0.

## Future Roadmap

- Product rule packs with precedence and provenance.
- Semantic and AI-assisted matchers behind the `RuleMatcher` interface.
- Advisory CI report generation.
- Configurable policy modes.
- Exception workflow.
- Knowledge Packs for reusable enterprise and product governance distribution.
- VS Code, GitHub App, and multi-agent integrations.

## Acknowledgements

ESF builds on GitHub Spec Kit and its Spec-Driven Development workflow. The v1.0 governance foundation is designed for enterprise teams that need consistent delivery evidence without losing the speed and flexibility of AI-assisted development.
