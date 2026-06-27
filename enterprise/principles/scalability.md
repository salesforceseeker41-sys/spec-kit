# Scalability Principles

## Purpose

This document defines enterprise scalability expectations for feature specifications and implementation plans.

## Ownership

Primary owner: Platform Architecture

Contributors:

- Site Reliability Engineering
- Salesforce Center of Excellence
- Data Architecture
- Product Engineering

## How This File Is Used

Use this file when planning workload growth, platform limits, data volume, integration throughput, batch processing, and operational resilience. It should help teams express scale in business terms before choosing technical mechanisms.

## Scalability Inputs Template

For each feature, document:

- Expected user population.
- Peak and average transaction volume.
- Data volume growth over time.
- Integration frequency and payload size.
- Batch, scheduled, or asynchronous workload needs.
- Latency expectations from the user's perspective.
- Operational recovery expectations.

## Principles

1. Define scale assumptions before selecting implementation patterns.
2. Prefer asynchronous processing when synchronous work is not user-critical.
3. Design around known platform limits instead of discovering them in production.
4. Use bulk-safe patterns for data processing.
5. Keep user-facing workflows responsive under expected peak load.
6. Plan observability for capacity, latency, errors, and backlogs.

## Salesforce-Specific Considerations

- Governor limits for Apex, Flow, SOQL, DML, CPU, heap, and callouts.
- Bulk data operations and record-triggered automation.
- Platform Event, Change Data Capture, Queueable, Batch, and Scheduled Apex usage.
- Sharing recalculation, large data volumes, and reporting performance.
- Deployment and test runtime at enterprise scale.

## Review Questions

- What is the expected peak usage pattern?
- What happens when upstream or downstream systems slow down?
- Which operations must be bulk-safe?
- What limits could the design hit first?
- What telemetry will show capacity risk early?
