# ESF Project Bootstrap

## Purpose

The ESF Project Bootstrap profile lets product teams create an enterprise-ready Salesforce Spec Kit project in one command:

```bash
specify init my-project --integration codex --profile salesforce-enterprise
```

The profile is additive. Standard `specify init my-project --integration codex` behavior is unchanged when `--profile` is omitted.

## Architecture

```text
specify init
  |
  v
standard Spec Kit scaffold
  |
  v
optional profile installer
  |
  v
enterprise Salesforce scaffold
```

The profile installer copies bundled files from `profiles/salesforce-enterprise/` after the normal Spec Kit scaffold is installed. Existing files are preserved unless `--force` is used.

## Generated Structure

```text
my-project/
|-- .specify/
|-- .agents/
|-- enterprise/
|   |-- constitution.md
|   |-- principles/
|   |-- salesforce/
|   `-- rules/
|-- products/
|   `-- sample-product/
|-- docs/
|   `-- esf-onboarding.md
|-- specs/
`-- enterprise.yaml
```

## Profile Configuration

The generated `enterprise.yaml` starts with:

```yaml
enterprise:
  version: 1.0

platform:
  name: Salesforce

product:
  name: sample-product

context:
  loadEnterprise: true
  loadProduct: true

governance:
  matcher: keyword
```

## Ownership

| Area | Owner | Purpose |
| --- | --- | --- |
| `enterprise/` | Platform Team | Enterprise constitution, principles, Salesforce standards, and rules. |
| `products/sample-product/` | Product Team | Product-specific domain, integration, and event guidance. |
| `specs/` | Delivery Team | Feature specifications, plans, tasks, and governance reports. |
| `.specify/` | Spec Kit | Core workflows, templates, scripts, and integration metadata. |

## Backward Compatibility

- `--profile` is optional.
- Only `salesforce-enterprise` is supported in v1.2.
- Existing init behavior, command names, integrations, validators, matchers, and governance engine behavior are unchanged.
- Invalid profile names fail clearly before project creation.

## Limitations

- The profile copies starter governance files into the project; it does not sync future enterprise updates.
- Knowledge-pack sync, remote rule fetching, CI/CD, and blocking governance are future capabilities.
- Product teams should rename `products/sample-product/` and update `enterprise.yaml` after initialization.
