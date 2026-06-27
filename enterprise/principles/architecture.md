# Architecture Principles

## Purpose

This document defines enterprise architecture expectations for product and feature planning. It helps teams keep feature-level decisions aligned with the long-term platform and product architecture.

## Ownership

Primary owner: Enterprise Architecture

Contributors:

- Solution Architecture
- Product Architecture
- Platform Engineering
- Salesforce Center of Excellence

## How This File Is Used

Use this file during `/plan` and architecture review to evaluate whether the proposed design fits enterprise standards, product boundaries, integration patterns, and operational ownership.

## Architecture Decision Template

Document material architecture decisions with:

- Decision.
- Business capability supported.
- Context and constraints.
- Options considered.
- Selected approach.
- Tradeoffs.
- Risks and mitigations.
- Owner and review date.

## Principles

1. Model business capabilities before implementation components.
2. Keep domain ownership clear across products and systems.
3. Prefer reusable platform capabilities over one-off implementations.
4. Make integration contracts explicit and version-aware.
5. Design for operations, observability, and support from the start.
6. Avoid hidden coupling through shared data, automation side effects, or undocumented dependencies.

## Review Questions

- What business capability does this feature change?
- Which product or platform owns the affected data?
- What systems are upstream and downstream?
- What contract or event describes the integration?
- How will support teams diagnose failure after release?

## Evidence Expected

- Product/domain alignment in `spec.md`.
- Technical approach and tradeoffs in `plan.md`.
- Integration and observability tasks in `tasks.md`.
