"""Governance execution statistics used by reports and engines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionStatistics:
    rules_loaded: int = 0
    rules_evaluated: int = 0
    rules_passed: int = 0
    rules_with_findings: int = 0
    documents_evaluated: int = 0
    execution_time_ms: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "rules_loaded": self.rules_loaded,
            "rules_evaluated": self.rules_evaluated,
            "rules_passed": self.rules_passed,
            "rules_with_findings": self.rules_with_findings,
            "documents_evaluated": self.documents_evaluated,
            "execution_time_ms": self.execution_time_ms,
        }

