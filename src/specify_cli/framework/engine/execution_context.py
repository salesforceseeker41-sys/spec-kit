"""Governance Engine execution context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ...enterprise_context import ContextBundle
from ...rule_catalog import RuleCatalog

Artifact = Literal["specification", "plan", "tasks", "all"]


@dataclass(frozen=True)
class ExecutionContext:
    context_bundle: ContextBundle
    rule_catalog: RuleCatalog
    artifact: Artifact
    feature_path: str | None = None
    product_name: str | None = None

    def resolved_feature_path(self) -> str | None:
        return self.feature_path or self.context_bundle.feature_path

    def resolved_product_name(self) -> str | None:
        return self.product_name or self.context_bundle.product_name

