# Architecture Principles

## Purpose

Define enterprise architecture expectations for Salesforce solutions.

## Ownership

Owned by the Platform Team. Delivery teams consume these standards when writing feature specifications and implementation plans.

## Starter Guidance

- Prefer platform capabilities before custom code.
- Keep domain logic explicit and testable.
- Use integration boundaries that are observable, retryable, and idempotent.
- Avoid feature-level architecture decisions that conflict with enterprise patterns.
- Document tradeoffs when a feature requires an exception.
