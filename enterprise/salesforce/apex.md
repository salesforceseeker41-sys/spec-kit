# Salesforce Apex Standards

## Purpose

This document defines starter enterprise standards for Apex design and implementation planning.

## Ownership

Primary owner: Salesforce Center of Excellence

Contributors:

- Salesforce Platform Engineering
- Application Security
- Product Engineering

## How This File Is Used

Use this file when a feature plan includes Apex classes, triggers, asynchronous jobs, integrations, or service-layer logic. Future governance checks can use it to validate that Apex work is bulk-safe, secure, testable, and operationally visible.

## Planning Template

For each Apex feature, document:

- Apex entry points: trigger, controller, invocable action, batch, queueable, scheduler, service class.
- Objects and fields accessed.
- Sharing model and user context.
- Expected record volume.
- Callouts or external dependencies.
- Error handling and retry strategy.
- Test data and test coverage approach.

## Standards

1. Keep triggers thin and delegate business logic to services.
2. Write bulk-safe logic for all record operations.
3. Avoid SOQL, DML, and callouts inside unbounded loops.
4. Respect sharing and field-level security where user context matters.
5. Use asynchronous Apex for long-running or integration-heavy work.
6. Make integration failures observable and recoverable.
7. Prefer explicit domain/service boundaries over utility-class sprawl.

## Review Questions

- What governor limits are most relevant to this design?
- Does the logic process one record and many records correctly?
- What user context does the code run under?
- How are errors surfaced to users or operations?
- What tests prove bulk behavior and security behavior?
