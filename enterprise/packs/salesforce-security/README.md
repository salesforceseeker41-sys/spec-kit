# Enterprise Salesforce Security Knowledge Pack

## Purpose

The Enterprise Salesforce Security Knowledge Pack defines enterprise-approved
Salesforce security rules for product teams building on the platform. It is a
governed rule pack for the Enterprise Spec Framework and is intended for
specification, planning, implementation, review, and future validation flows.

## Scope

This pack covers:

- CRUD/FLS enforcement
- Sharing and Apex sharing modes
- `Security.stripInaccessible`
- `WITH SECURITY_ENFORCED`
- Named Credentials and secrets management
- OAuth, Connected Apps, and session controls
- Guest user access
- Encryption, Shield, audit logging, and Event Monitoring
- Permission Sets and least privilege
- CSP, Locker, and Lightning Web Security

## Rule Location

Rules are stored in:

```text
enterprise/salesforce/security/rules.yaml/
```

Rule IDs use the `SFSEC-` prefix.

## Ownership

Primary owner: Enterprise Salesforce Security Architecture

Contributors:

- Salesforce Center of Excellence
- Platform Engineering
- Identity and Access Management
- Compliance and Risk
- Observability / SRE

## Lifecycle

Rules start as advisory unless explicitly marked as warning or blocking. Product
teams may request exceptions through the enterprise exception process, but rule
IDs are stable and must not be reused after retirement.
