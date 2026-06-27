# RDRA Events

## Purpose

This document defines the starter event catalog for RDRA. Events describe meaningful business changes that other systems, automations, or processes may need to observe.

## Ownership

Primary owner: RDRA Architecture Owner

Contributors:

- Event Producers and Consumers
- Integration Architecture
- Salesforce Platform Engineering
- Product Engineering

## How This File Is Used

Use this file when planning event-driven features, integration changes, audit requirements, or asynchronous Salesforce patterns such as Platform Events and Change Data Capture.

## Event Definition Template

For each event, document:

- Event name.
- Business meaning.
- Producer and owner.
- Consumers and owners.
- Triggering condition.
- Payload fields.
- Data classification.
- Ordering, replay, and idempotency expectations.
- Error handling and dead-letter strategy.
- Versioning approach.

## Event Catalog

| Event | Producer | Consumers | Status | Notes |
|-------|----------|-----------|--------|-------|
| TBD | TBD | TBD | Candidate | Replace with RDRA product events as they are identified. |

## Event Principles

1. Events should represent business facts that already happened.
2. Payloads should be minimal, stable, and version-aware.
3. Consumers should be idempotent.
4. Event ownership must be explicit.
5. Sensitive data should not be included unless required and approved.
