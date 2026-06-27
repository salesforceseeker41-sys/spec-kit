# RDRA Product Principles

## Purpose

This document is the product-level governance starting point for RDRA. It adapts enterprise principles to the product context while preserving traceability to `enterprise/constitution.md`.

## Ownership

Primary owner: RDRA Product Owner

Contributors:

- RDRA Architecture Owner
- RDRA Engineering Lead
- Enterprise Architecture
- Salesforce Center of Excellence

## How This File Is Used

Feature specifications for RDRA should reference this file to explain product-specific constraints, priorities, and non-negotiable behaviors. Governance checks should use it alongside enterprise principles.

## Product Mission

RDRA provides governed, reliable, and auditable capabilities for its product domain. The product should favor clarity, traceability, and operational confidence over short-term customization shortcuts.

## Product Principles

1. RDRA features must align to a named business capability.
2. Product data ownership must be clear before integrations replicate or transform data.
3. User-facing workflows should remain explainable to business owners and support teams.
4. Automation must be observable and recoverable.
5. Integrations should use explicit contracts, documented events, and named owners.
6. Salesforce customizations should stay within enterprise platform standards.

## Feature Intake Template

For each RDRA feature, capture:

- Business capability.
- Primary users.
- Data domains affected.
- Integrations affected.
- Compliance or audit considerations.
- Operational owner.
- Expected release path.
