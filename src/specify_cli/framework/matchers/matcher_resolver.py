"""Resolve governance matcher selection from CLI and enterprise config."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..exceptions import ConfigurationError
from .base import RuleMatcher
from .keyword_matcher import KeywordMatcher
from .practice_compliance_matcher import PracticeComplianceMatcher

SUPPORTED_MATCHERS = ("keyword", "practice")


class MatcherResolver:
    """Resolve the selected matcher while preserving keyword as the default."""

    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path)

    def resolve(self, requested: str | None = None) -> RuleMatcher:
        name = (requested or self._configured_matcher() or "keyword").strip().lower()
        if name == "keyword":
            return KeywordMatcher()
        if name == "practice":
            return PracticeComplianceMatcher()
        raise ConfigurationError(
            f"Unsupported governance matcher '{name}'. Supported matchers: {', '.join(SUPPORTED_MATCHERS)}."
        )

    def _configured_matcher(self) -> str | None:
        config_path = self.root_path / "enterprise.yaml"
        if not config_path.is_file():
            return None
        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigurationError(
                f"Could not read governance matcher configuration: {exc}"
            ) from exc
        if not isinstance(raw, dict):
            return None

        governance = raw.get("governance")
        if not isinstance(governance, dict):
            return None
        matcher = governance.get("matcher")
        if isinstance(matcher, str):
            return matcher
        if isinstance(matcher, dict):
            selected = matcher.get("default") or matcher.get("name")
            if isinstance(selected, str):
                return selected
        return None
