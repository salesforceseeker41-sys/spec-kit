# Security Principles

## Purpose

This document defines enterprise security expectations for features planned with Spec Kit. It should guide requirements, architecture plans, and implementation tasks before code is written.

## Ownership

Primary owner: Security Architecture

Consulted teams:

- Identity and Access Management
- Application Security
- Salesforce Platform Security
- Product Engineering

## How This File Is Used

Governance reviews should use this file to check whether a feature has identified authentication, authorization, data protection, auditability, and threat-modeling concerns. Future enterprise extension commands may use these sections as validation prompts.

## Security Requirements Template

For each feature, document:

- Users, roles, and permission boundaries.
- Authentication assumptions.
- Authorization rules at object, record, field, and action levels.
- Sensitive data read, written, transmitted, or derived.
- Audit events that must be captured.
- External systems or trust boundaries crossed.
- Abuse cases or misuse scenarios.

## Principles

1. Apply least privilege to users, integrations, automation, and service accounts.
2. Treat customer, employee, financial, and regulated data as sensitive by default.
3. Enforce authorization at the system boundary and within domain operations.
4. Prefer platform-managed identity, secrets, encryption, and audit features.
5. Log security-relevant events without exposing sensitive data in logs.
6. Require explicit review for public endpoints, guest access, and elevated automation.

## Review Questions

- What data can the feature expose, modify, export, or delete?
- Who can perform each privileged action?
- What prevents a user from accessing another user's data?
- What secrets, tokens, certificates, or credentials are involved?
- What security event would prove misuse or unauthorized access?

## Evidence Expected

- Security requirements in `spec.md`.
- Authorization and trust-boundary decisions in `plan.md`.
- Security tasks in `tasks.md`.
- Exception notes for any unresolved risk.
