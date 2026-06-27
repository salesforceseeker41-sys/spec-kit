# Salesforce Lightning Web Components Standards

## Purpose

This document defines starter enterprise standards for Lightning Web Components.

## Ownership

Primary owner: Salesforce UX and Platform Engineering

Contributors:

- Salesforce Center of Excellence
- Accessibility Reviewers
- Product Engineering
- Security Architecture

## How This File Is Used

Use this file when planning user-facing Salesforce experiences. It should guide usability, accessibility, data access, state management, and integration with Apex or UI APIs.

## Planning Template

For each LWC feature, document:

- Target users and page context.
- Components added or modified.
- Data sources and write operations.
- Error, loading, and empty states.
- Accessibility considerations.
- Permission and visibility behavior.
- Test strategy.

## Standards

1. Prefer Lightning Data Service and UI APIs when they meet the need.
2. Use Apex only when platform APIs cannot support the use case cleanly.
3. Design accessible keyboard, screen reader, and focus behavior.
4. Avoid exposing sensitive data in client-side state or browser logs.
5. Keep components small, composable, and owned by clear product boundaries.
6. Provide useful error and empty states for business users.
7. Validate user permissions before exposing actions or data.

## Review Questions

- What user problem does the component solve?
- What data is visible, editable, or submitted?
- How does the component behave for users with limited permissions?
- What happens when data loading fails?
- How is accessibility verified?
