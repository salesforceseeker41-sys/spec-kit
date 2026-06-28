# Scalability Principles

## Purpose

Define expectations for Salesforce scale, large data volume behavior, governor limits, and operational resilience.

## Ownership

Owned by the Platform Team.

## Starter Guidance

- Design Apex for bulk processing by default.
- Avoid SOQL and DML inside loops.
- Plan for governor limits, record locking, and batch sizes.
- Use asynchronous processing when synchronous work would exceed safe limits.
- Include bulk and large data volume test scenarios.
