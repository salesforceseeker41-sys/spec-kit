# Salesforce Deployment Standards

## Purpose

This document defines starter enterprise guidance for Salesforce deployment planning and release readiness.

## Ownership

Primary owner: Release Management

Contributors:

- Salesforce Platform Engineering
- DevOps
- Quality Engineering
- Product Owners

## How This File Is Used

Use this file when planning tasks for metadata changes, data migrations, permission changes, integrations, or feature activation. It should help teams capture deployment sequencing, validation, rollback, and communication needs.

## Deployment Planning Template

For each Salesforce release, document:

- Metadata components changed.
- Data migration or backfill steps.
- Permission set, profile, sharing, or license changes.
- Feature flags or activation steps.
- Environment promotion path.
- Pre-deployment and post-deployment validation.
- Rollback or mitigation plan.
- Release owner and support contact.

## Standards

1. Separate deployable metadata from manual activation where possible.
2. Treat permission and sharing changes as release-critical.
3. Include smoke tests that validate the business capability after deployment.
4. Document data migration idempotency and recovery.
5. Coordinate integration changes with upstream and downstream owners.
6. Avoid production-only configuration knowledge.

## Review Questions

- What must happen before deployment starts?
- What can be rolled back automatically?
- What requires manual verification?
- What users or systems need release communication?
- What monitoring should be watched immediately after release?
