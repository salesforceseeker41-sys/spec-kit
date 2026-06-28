# Enterprise Salesforce Integration Knowledge Pack

## Purpose

The Enterprise Salesforce Integration Knowledge Pack defines enterprise-approved
rules for Salesforce integrations. It extends the Enterprise Spec Framework with
integration-specific governance for design, implementation planning, review,
testing, deployment, and operations.

## Scope

This pack covers Named Credentials, REST, SOAP, Platform Events, Change Data
Capture, middleware, idempotency, retry, timeout, error handling, logging,
monitoring, and security.

## Rule Location

Rules are stored in:

```text
enterprise/rules/salesforce-integration/
```

Rule IDs use the `SFINT-` prefix.

## Ownership

Primary owner: Integration Architecture

Contributors:

- Salesforce Center of Excellence
- Enterprise Architecture
- Salesforce Security Architecture
- Platform Engineering
- Observability / SRE

## Lifecycle

Rules are advisory, warning, or blocking according to delivery risk. Product
teams may request exceptions through the enterprise exception process, but rule
IDs are stable and must not be reused after retirement.
