# Salesforce Flow Standards

## Purpose

This document defines starter enterprise standards for Salesforce Flow usage.

## Ownership

Primary owner: Salesforce Center of Excellence

Contributors:

- Business Process Owners
- Salesforce Administrators
- Platform Engineering
- Quality Engineering

## How This File Is Used

Use this file when a feature includes record-triggered flows, screen flows, scheduled flows, orchestration, or invocable automation. It helps decide when Flow is appropriate and what evidence is needed for safe operation.

## Planning Template

For each Flow change, document:

- Flow type and trigger.
- Business process owner.
- Objects and fields read or updated.
- Entry criteria and exit criteria.
- Error paths and fault handling.
- Interaction with Apex, validation rules, and other automation.
- Test scenarios and activation plan.

## Standards

1. Use Flow for declarative business process automation where it remains understandable and maintainable.
2. Keep record-triggered flows bulk-safe and selective.
3. Avoid overlapping automation that creates hidden order-of-execution behavior.
4. Include fault paths for data changes and external actions.
5. Document activation, deactivation, and rollback steps.
6. Review complex flows for Apex or platform-event alternatives.

## Review Questions

- Who owns the business process represented by the Flow?
- What other automation runs on the same object?
- Can the Flow handle bulk data updates?
- How are errors captured and remediated?
- What rollback path exists if the Flow causes production issues?
