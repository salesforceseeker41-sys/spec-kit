# RDRA Domain Model

## Purpose

This document defines the starter domain model workspace for RDRA. It is intended to capture business entities, relationships, ownership, and vocabulary before technical schemas are finalized.

## Ownership

Primary owner: RDRA Product Architecture

Contributors:

- Business Domain Experts
- Data Architecture
- Salesforce Architecture
- Product Engineering

## How This File Is Used

Use this file during `/specify` and `/plan` work to keep feature artifacts aligned with RDRA's shared domain language. Feature-level `data-model.md` files should link back to relevant product entities and explain any additions or changes.

## Domain Vocabulary Template

For each domain concept, document:

- Name.
- Business definition.
- Owner.
- Source of record.
- Key attributes.
- Lifecycle states.
- Related entities.
- Sensitive or regulated data classification.
- Events emitted or consumed.

## Starter Domain Concepts

| Concept | Definition | Owner | Source of Record | Notes |
|---------|------------|-------|------------------|-------|
| TBD | Product domain concept to define. | TBD | TBD | Replace with RDRA-specific concepts. |

## Modeling Principles

1. Use business language before object or table names.
2. Identify source of record for each entity.
3. Make lifecycle state explicit.
4. Document ownership before sharing or replication.
5. Treat events as part of the domain model, not only integration plumbing.
