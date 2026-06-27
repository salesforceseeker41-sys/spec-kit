# Compliance Principles

## Purpose

This document defines starter compliance guidance for features that handle regulated data, audit obligations, retention requirements, or policy-controlled business processes.

## Ownership

Primary owner: Compliance and Risk

Contributors:

- Legal
- Data Governance
- Security Architecture
- Product Owners
- Enterprise Architecture

## How This File Is Used

Use this file to determine whether a feature needs compliance review and what evidence should be captured in the specification, implementation plan, and tasks.

## Compliance Classification Template

For each governed feature, document:

- Applicable regulation, policy, or contractual obligation.
- Data classification and data subjects.
- Consent, retention, deletion, and access requirements.
- Audit events and reporting needs.
- Geographic, residency, or cross-border processing constraints.
- Required approvals before release.

## Principles

1. Classify data before designing storage, sharing, or integration behavior.
2. Capture auditability requirements as functional requirements.
3. Make retention and deletion expectations explicit.
4. Minimize regulated data collection and replication.
5. Document evidence in repository artifacts, not only in external tickets.
6. Treat compliance exceptions as risk decisions with named owners.

## Review Questions

- What regulated or policy-controlled data is involved?
- Is the feature creating a new system of record or derived record?
- What must be auditable after release?
- How long must data be retained?
- Who can approve an exception?

## Evidence Expected

- Compliance classification in the feature spec.
- Data handling decisions in the plan.
- Audit, retention, and validation tasks in the task list.
