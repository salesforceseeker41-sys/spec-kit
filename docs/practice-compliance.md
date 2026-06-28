# Salesforce Practice Compliance

## Purpose

Salesforce Practice Compliance is the Enterprise Spec Framework v1.1 capability for checking whether feature specifications, plans, and tasks show evidence of enterprise Salesforce practices.

It is different from simple keyword matching. Keyword matching asks whether text contains a term. Practice compliance asks whether an artifact provides enough deterministic evidence that a Salesforce practice is addressed.

Examples:

- Apex bulkification evidence: records processed in collections, SOQL and DML outside loops, map or set usage, and bulk tests.
- Security evidence: CRUD/FLS, sharing model, permission checks, `stripInaccessible`, `WITH SECURITY_ENFORCED`, and least privilege.
- Integration evidence: Named Credentials, timeout handling, retry strategy, idempotency, logging, and error recovery.

## Advisory-Only Behavior

Practice Compliance is advisory only.

- It does not block delivery.
- It does not introduce critical or blocking severities.
- Confidence is guidance, not approval.
- Findings should be read as "may not be fully evidenced" rather than "non-compliant."

## Matcher Selection

`KeywordMatcher` remains the default matcher.

Practice Compliance is opt-in:

```bash
python scripts/validate-governance.py --feature specs/001-provider-program --matcher practice
```

The optional enterprise configuration is:

```yaml
governance:
  matcher: keyword
```

or:

```yaml
governance:
  matcher: practice
```

CLI matcher selection overrides `enterprise.yaml`.

## Rule Schema Fields

Practice Compliance uses additive rule fields. Existing rules remain valid.

```yaml
practice:
  type: salesforce_apex_bulkification
  min_confidence: 0.7

required_evidence:
  - processes records in collections
  - avoids SOQL inside loops
  - avoids DML inside loops

negative_evidence:
  - DML inside loop

evidence_terms:
  processes records in collections:
    - collections
    - bulk records
  avoids SOQL inside loops:
    - query outside loop
    - no SOQL inside loop
  DML inside loop:
    - DML inside loop
    - update inside loop
```

## Confidence

Confidence is deterministic:

```text
matched required evidence / total required evidence
```

Negative evidence reduces confidence. The final value is clamped between `0.0` and `1.0`.

Confidence is included in reports so delivery teams can see how much evidence was found. It is not an enforcement decision.

## Report Metadata

Reports include matcher metadata:

- matcher name
- matcher version
- confidence
- matched evidence
- missing evidence
- negative evidence
- explanation

JSON reports are suitable for future CI/CD and multi-agent integrations.

## Privacy Posture

v1.1 is local-only.

- No LLM matching.
- No external API calls.
- No embeddings.
- No telemetry.
- No artifact upload.

This is intentional because specifications and plans may contain sensitive architecture, integration, business, or customer information.

## Future AI-Assisted Reasoning

Future versions may add LLM-assisted or semantic reasoning behind the same `RuleMatcher` abstraction. Any such capability should be explicit opt-in, governed by enterprise privacy policy, and should preserve deterministic local fallback.
