# Enterprise Constitution

## Purpose

This constitution defines the enterprise decision framework for Salesforce delivery. It is owned by the Platform Team and applies to every product and delivery team using this project.

## Ownership

- Platform Team owns enterprise architecture, security, compliance, shared Salesforce standards, and rule packs.
- Product Teams own product-specific domain rules under `products/<product>/`.
- Delivery Teams own feature requirements, implementation plans, and tasks under `specs/`.

## Usage

AI agents, validators, and reviewers should consider this file before product or feature guidance. Delivery teams should reference this constitution when creating specifications and plans, but should not redefine enterprise architecture inside feature artifacts.

## Decision Principles

1. Enterprise standards are mandatory unless an approved exception exists.
2. Product standards are mandatory for the selected product.
3. Salesforce solutions must be secure by default and least-privilege by design.
4. Features must describe integration, data, testing, deployment, and operational impact.
5. Governance feedback is advisory unless the organization enables blocking validation in a future release.
