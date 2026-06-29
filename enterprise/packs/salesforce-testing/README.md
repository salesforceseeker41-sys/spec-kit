# Enterprise Salesforce Testing Knowledge Pack

## Purpose

The Enterprise Salesforce Testing Knowledge Pack defines enterprise-approved
testing rules for Salesforce product teams. It extends the Enterprise Spec
Framework with testing-specific governance for Apex, Flow, integrations,
security, bulk behavior, governor limits, test isolation, mocking, coverage,
and negative testing.

## Scope

This pack covers Apex tests, Flow tests, bulk tests, security tests,
integration tests, governor limit tests, test isolation, test data factories,
mocking, code coverage, and negative testing.

## Rule Location

Rules are stored in:

```text
enterprise/salesforce/testing/rules.yaml/
```

Rule IDs use the `SFTEST-` prefix.

## Ownership

Primary owner: Quality Engineering

Contributors:

- Salesforce Center of Excellence
- Salesforce Security Architecture
- Platform Engineering
- Integration Architecture
- Release Management

## Lifecycle

Rules are advisory, warning, or blocking according to delivery risk. Product
teams may request exceptions through the enterprise exception process, but rule
IDs are stable and must not be reused after retirement.
