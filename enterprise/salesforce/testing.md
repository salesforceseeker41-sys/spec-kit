# Salesforce Testing Standards

## Purpose

This document defines starter enterprise expectations for testing Salesforce features.

## Ownership

Primary owner: Quality Engineering

Contributors:

- Salesforce Center of Excellence
- Product Engineering
- Release Management
- Security Architecture

## How This File Is Used

Use this file during task generation to ensure Salesforce features include meaningful unit, integration, security, automation, and release validation tasks.

## Test Planning Template

For each feature, document:

- Critical user scenarios.
- Apex unit tests and negative tests.
- Flow test coverage or documented manual validation.
- LWC unit or UI validation needs.
- Integration contract validation.
- Permission and sharing tests.
- Regression and deployment validation steps.

## Standards

1. Tests should prove business behavior, not only line coverage.
2. Apex tests must create their own data and avoid org data dependencies.
3. Include bulk and boundary tests for automation.
4. Validate permission-sensitive behavior with appropriate users or profiles.
5. Test integrations through contracts, mocks, or controlled sandboxes.
6. Include deployment smoke tests for high-risk changes.

## Review Questions

- What test proves the highest-value user story works?
- What test proves unauthorized users cannot perform restricted actions?
- What test proves bulk behavior?
- What deployment validation is required before release?
- What regression area is most likely to break?
