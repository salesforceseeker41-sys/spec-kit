# Enterprise Spec Framework Compatibility Matrix

## Purpose

This matrix documents the supported compatibility surface for Enterprise Spec Framework (ESF) v1.0. ESF is additive to GitHub Spec Kit and should not change existing Spec Kit command behavior.

## GitHub Spec Kit Compatibility

| Area | v1.0 status | Notes |
| --- | --- | --- |
| Spec Kit CLI | Compatible | ESF adds scripts and package modules without changing `specify` command behavior. |
| `/speckit.specify` | Compatible | Prompt guidance is additive and keeps the existing workflow. |
| `/speckit.plan` | Compatible | Prompt guidance is additive and keeps the existing workflow. |
| `/speckit.tasks` | Compatible | Prompt guidance is additive and keeps the existing workflow. |
| Existing templates | Compatible | ESF does not rename core commands. |
| Existing project initialization | Compatible | `specify init` behavior is unchanged. |

## Python Version

| Runtime | v1.0 status | Notes |
| --- | --- | --- |
| Python 3.11+ | Supported | Matches the repository development guidance. |
| Python 3.10 and earlier | Not certified | ESF uses modern type syntax consistent with the current codebase. |

## Operating Systems

| OS | v1.0 status | Notes |
| --- | --- | --- |
| Windows | Supported | Validated with PowerShell in this working tree. |
| macOS | Expected compatible | Uses Python standard library and repository conventions. |
| Linux | Expected compatible | Uses Python standard library and repository conventions. |

Windows test note: some upstream Spec Kit tests exercise symlink behavior or agent-specific home-directory writes. Those tests may require Developer Mode, elevated symlink privileges, or isolated home-directory configuration. ESF's own loaders, rule catalog, engine, and validator do not require symlink privileges.

## AI Coding Agents

| Agent surface | v1.0 status | Notes |
| --- | --- | --- |
| GitHub Copilot | Compatible | Consumes additive prompt guidance through existing Spec Kit integration behavior. |
| Claude | Compatible | Consumes additive prompt guidance through existing Spec Kit integration behavior. |
| Codex | Compatible | Consumes additive prompt guidance through existing Spec Kit integration behavior. |
| Gemini | Compatible | Consumes additive prompt guidance through existing Spec Kit integration behavior. |
| Other Spec Kit integrations | Expected compatible | ESF keeps command names and workflow unchanged. |

## Enterprise Governance Packs

| Pack type | v1.0 status | Notes |
| --- | --- | --- |
| Enterprise governance docs | Supported | Stored under `enterprise/`. |
| Salesforce standards | Supported | Stored under `enterprise/salesforce/`. |
| Enterprise rule packs | Supported | Stored under `enterprise/salesforce/<domain>/rules.yaml`. |
| Product standards | Supported | Stored under `products/<product-name>/`, selected by `enterprise.yaml`. |
| Product rule packs | Planned | Precedence and conflict handling are future work. |
| Knowledge Packs | Planned | Packaging and upgrade workflows are future work. |

## Future Semantic Matching

| Capability | v1.0 status | Notes |
| --- | --- | --- |
| Keyword matching | Supported | Implemented by `KeywordMatcher`. |
| Regex matching | Planned | Should implement the `RuleMatcher` interface. |
| Semantic matching | Planned | Should implement the `RuleMatcher` interface. |
| AI-assisted matching | Planned | Should implement the `RuleMatcher` interface and preserve report structure. |
| Blocking policy | Planned | Should be introduced as a policy layer, not by changing matchers. |

## Public API Stability

The v1.0 stable extension points are:

- `ContextLoader`
- `ContextBundle`
- `RuleLoader`
- `RuleCatalog`
- `GovernanceEngine`
- `ExecutionContext`
- `ExecutionStatistics`
- `RuleMatcher`
- `KeywordMatcher`
- `GovernanceReport`
- `GovernanceFinding`

Internal helpers, script implementation details, and module-level constants are not stable APIs.
