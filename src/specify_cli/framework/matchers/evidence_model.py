"""Evidence result structures for deterministic practice compliance matching."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceResult:
    """Deterministic evidence evaluation result for one practice rule."""

    matched_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    negative_evidence_found: list[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""

