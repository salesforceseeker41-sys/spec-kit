# Enterprise Spec Framework Onboarding

## Purpose

This project was initialized with the `salesforce-enterprise` bootstrap profile. The scaffold gives teams a consistent starting point for enterprise Salesforce governance while preserving the standard Spec Kit workflow.

## Folder Ownership

| Folder | Owner | Purpose |
| --- | --- | --- |
| `.specify/` | Spec Kit | Core templates, workflows, scripts, and agent configuration. |
| `enterprise/` | Platform Team | Enterprise constitution, principles, Salesforce standards, and rule packs. |
| `products/sample-product/` | Product Team | Product-specific domain standards and integration context. |
| `specs/` | Delivery Teams | Feature specifications, implementation plans, tasks, and governance reviews. |
| `docs/` | Shared | Human-readable onboarding and project documentation. |

## Development Lifecycle

1. Product Team updates `products/sample-product/` with product-specific standards.
2. Delivery Team uses `/speckit.specify` to create feature requirements.
3. Delivery Team uses `/speckit.plan` to describe implementation approach.
4. Delivery Team uses `/speckit.tasks` to generate actionable tasks.
5. Advisory governance tools review artifacts against enterprise and product context.
6. Findings are treated as recommendations unless your organization enables blocking validation in a future release.

## First Adoption Steps

1. Rename `products/sample-product/` to your product identifier.
2. Update `enterprise.yaml` so `product.name` matches the product folder.
3. Review `enterprise/` with the Platform Team.
4. Populate product domain, integration, and event documentation.
5. Start new feature work under `specs/`.
