# Enterprise Context Loader

## Purpose

The Enterprise Context Loader is the deterministic discovery layer for the Enterprise Governance scaffold. It reads `enterprise.yaml`, resolves the selected product, loads governance documents in a stable order, and returns a structured Context Bundle.

The loader does not validate governance rules, block delivery, register hooks, or invoke AI agents. It only makes governance context discoverable, ordered, and reusable for future prompt builders, advisory validators, and multi-agent integrations.

## Architecture

```text
scripts/load-enterprise-context.py
  |
  v
specify_cli.enterprise_context.ContextLoader
  |
  v
ContextBundle
  |
  +-- EnterpriseConfig
  +-- ContextDocument[]
  +-- warnings
  +-- errors
```

Core concepts:

- `EnterpriseConfig`: normalized values from `enterprise.yaml`.
- `ContextDocument`: one loaded or missing document, including path, title, category, layer, content, and warnings.
- `ContextBundle`: the final structured result, including config, loaded documents, warnings, errors, root path, product name, and optional feature path.
- `ContextLoader`: the deterministic discovery and loading service.

## Config Fields

Required fields in `enterprise.yaml`:

```yaml
enterprise:
  version: "1.0"

platform:
  name: "Enterprise Spec Framework"

product:
  name: "rdra"
```

Optional fields:

```yaml
context:
  loadEnterprise: true
  loadProduct: true
```

Defaults:

- `context.loadEnterprise`: `true`
- `context.loadProduct`: `true`

If `enterprise.yaml` is missing, the loader returns a config object with enterprise and product loading disabled and emits a warning. If `enterprise.yaml` exists but is malformed, the loader returns errors and does not load governance documents.

## Context Loading Order

Documents are loaded in this deterministic order:

1. `enterprise/constitution.md`
2. `enterprise/principles/*.md`
3. `enterprise/salesforce/*.md`
4. `products/<product-name>/`
5. Feature specification, when explicitly provided

Files inside folders are sorted alphabetically. `enterprise/constitution.md` is always loaded before folder-based enterprise documents.

Product files use a product-specific deterministic order:

1. `principles.md`
2. `domain-model.md`
3. `business-rules.yaml`
4. `events.md`
5. `integrations.md`
6. Other `.md`, `.yaml`, or `.yml` files alphabetically

## Product Resolution

Sprint 2 resolves product context only from:

```yaml
product:
  name: "rdra"
```

The loader does not infer product from branch names, feature names, folder names, or user prompts. If `product.name` is missing, the loader emits a warning and skips product loading.

## Dynamic Product Context

Each Product Team owns its folder under `products/`. The active product is selected by `enterprise.yaml`:

```yaml
product:
  name: product-team1
```

or:

```yaml
product:
  name: rdra
```

At runtime, the context loader reads `products/<product-name>/` dynamically. Product context includes:

- `principles.md`
- `domain-model.md`
- `business-rules.yaml`
- `events.md`
- `integrations.md`
- Future `.md`, `.yaml`, or `.yml` files

If Product Team 1 updates:

```text
products/product-team1/domain-model.md
products/product-team1/events.md
products/product-team1/integrations.md
products/product-team1/business-rules.yaml
```

then future `/speckit-specify`, `/speckit-plan`, and `/speckit-implement` runs use the updated content automatically because the loader reads the configured product folder on each run.

Enterprise rules remain platform-owned under `enterprise/`. Product rules and business rules remain product-owned under `products/<product-name>/`.

## Feature Resolution

The loader accepts an optional feature path:

```bash
python scripts/load-enterprise-context.py --feature specs/001-provider-program
python scripts/load-enterprise-context.py --feature specs/001-provider-program/specification.md
```

If the input is a folder, the loader attempts to load `specification.md` from that folder. If the input is a file, the loader loads that file. If no feature path is provided, feature loading is skipped without warning. If a feature path is provided but the specification is missing, the loader emits a warning.

## CLI Examples

Default list output:

```bash
python scripts/load-enterprise-context.py
```

Include a feature:

```bash
python scripts/load-enterprise-context.py --feature specs/001-provider-program
```

Markdown output:

```bash
python scripts/load-enterprise-context.py --format markdown
```

JSON summary:

```bash
python scripts/load-enterprise-context.py --format json
```

Use an explicit root:

```bash
python scripts/load-enterprise-context.py --root . --format list
```

## Output Formats

### list

Prints loaded paths in deterministic order. Warnings and errors are written to stderr.

### markdown

Prints a deterministic markdown rendering of the Context Bundle, including bundle metadata, warnings, errors, and document sections.

### json

Prints a structured Context Bundle summary without document content. This is intended for scripts and future automation.

## Limitations

- No validation is performed.
- No rule engine exists yet.
- No blocking governance is introduced.
- No product aliases or multi-product support exist.
- No automatic hook registration is performed.
- No prompt execution or AI invocation is performed.
- Feature folder resolution looks for `specification.md` by design for Sprint 2.

## Future Roadmap

### Sprint 3: Enterprise Validation

Use the Context Bundle to run advisory checks against `spec.md`, `plan.md`, and `tasks.md`.

### Sprint 4: Rule Engine

Add structured rules, severities, exception metadata, and machine-readable validation results.

### Sprint 5: Knowledge Packs

Package enterprise standards, Salesforce standards, product context, and rules into reusable installable packs.
