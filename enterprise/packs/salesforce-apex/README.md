# Enterprise Salesforce Apex Knowledge Pack

## Purpose

The Enterprise Salesforce Apex Knowledge Pack defines enterprise-approved Apex engineering rules for Salesforce product teams. It extends the Enterprise Spec Framework with Apex-specific governance for design, implementation planning, review, and future automated validation.

## Scope

This pack covers trigger frameworks, bulkification, governor limits, collections, selectors, services, domains, asynchronous Apex, Platform Events, error handling, logging, dependency injection, unit testing, SOQL, DML, performance, caching, metadata, and configuration.

## Rule Location

Rules are stored in:

```text
enterprise/rules/salesforce-apex/
```

Rule IDs use the `SFAPEX-` prefix.

## Ownership

Primary owner: Salesforce Center of Excellence

Contributors:

- Enterprise Architecture
- Platform Engineering
- Salesforce Security Architecture
- DevOps Enablement
- Observability / SRE

## Lifecycle

Rules are advisory, warning, or blocking according to delivery risk. Product teams may request exceptions through the enterprise exception process, but rule IDs are stable and must not be reused after retirement.
