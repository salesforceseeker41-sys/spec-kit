# Flow Standards

## Purpose

Define standards for Salesforce Flow design, maintainability, and operational safety.

## Ownership

Owned by the Platform Team.

## Starter Guidance

- Prefer before-save record-triggered flows for simple field updates.
- Avoid duplicate automation for the same object and event.
- Use clear fault paths and logging.
- Keep flows bulk-safe and easy to troubleshoot.
- Document when Apex is more appropriate than Flow.
