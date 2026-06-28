"""Governance Engine execution result."""

from __future__ import annotations

from dataclasses import dataclass

from ..reports import GovernanceReport


@dataclass(frozen=True)
class ExecutionResult:
    report: GovernanceReport

