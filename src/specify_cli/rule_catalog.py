"""Machine-readable enterprise governance rule catalog.

Sprint 3.5 models rules as data. This module discovers and loads rule YAML
files, but it does not evaluate rules, match keywords, enforce severities, or
perform validation.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .enterprise_context import ContextLoader
from .framework.exceptions import RuleCatalogError


RULES_ROOT = Path("enterprise") / "rules"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Rule:
    """One machine-readable governance rule."""

    id: str
    title: str
    category: str
    description: str
    rationale: str
    severity: str
    default_enabled: bool
    applies_to: list[str]
    keywords: list[str]
    recommendation: str
    references: list[str]
    owner: str
    version: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], *, path: str) -> "Rule":
        """Create a rule from a YAML mapping.

        Unknown fields are preserved in ``metadata`` so the schema can evolve
        without breaking older loader consumers.
        """

        known_fields = {
            "id",
            "title",
            "category",
            "description",
            "rationale",
            "severity",
            "default_enabled",
            "applies_to",
            "keywords",
            "recommendation",
            "references",
            "owner",
            "version",
        }
        metadata = {key: value for key, value in data.items() if key not in known_fields}

        return cls(
            id=_string_value(data.get("id")),
            title=_string_value(data.get("title")),
            category=_string_value(data.get("category")),
            description=_string_value(data.get("description")),
            rationale=_string_value(data.get("rationale")),
            severity=_string_value(data.get("severity")),
            default_enabled=_bool_value(data.get("default_enabled")),
            applies_to=_string_list(data.get("applies_to")),
            keywords=_string_list(data.get("keywords")),
            recommendation=_string_value(data.get("recommendation")),
            references=_string_list(data.get("references")),
            owner=_string_value(data.get("owner")),
            version=_string_value(data.get("version")),
            path=path,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "rationale": self.rationale,
            "severity": self.severity,
            "default_enabled": self.default_enabled,
            "applies_to": list(self.applies_to),
            "keywords": list(self.keywords),
            "recommendation": self.recommendation,
            "references": list(self.references),
            "owner": self.owner,
            "version": self.version,
            "path": self.path,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


@dataclass(frozen=True)
class RuleCategory:
    """Rules grouped under one catalog category."""

    name: str
    slug: str
    rules: list[Rule]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "rules": [rule.to_dict() for rule in self.rules],
        }


@dataclass(frozen=True)
class RuleCollection:
    """Loaded rule set plus non-blocking loader diagnostics."""

    rules: list[Rule]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    root_path: str = ""

    def has_errors(self) -> bool:
        return bool(self.errors)

    def by_category(self) -> dict[str, list[Rule]]:
        grouped: dict[str, list[Rule]] = {}
        for rule in self.rules:
            grouped.setdefault(_slug(rule.category), []).append(rule)
        return {
            key: sorted(value, key=lambda rule: rule.id)
            for key, value in sorted(grouped.items())
        }

    def categories(self) -> list[RuleCategory]:
        return [
            RuleCategory(
                name=rules[0].category if rules else slug,
                slug=slug,
                rules=rules,
            )
            for slug, rules in self.by_category().items()
        ]

    def by_applies_to(self) -> dict[str, list[Rule]]:
        grouped: dict[str, list[Rule]] = {}
        for rule in self.rules:
            for target in rule.applies_to:
                grouped.setdefault(_slug(target), []).append(rule)
        return {
            key: sorted(value, key=lambda rule: rule.id)
            for key, value in sorted(grouped.items())
        }

    def filter_category(self, category: str) -> "RuleCollection":
        slug = _slug(category)
        rules = [rule for rule in self.rules if _slug(rule.category) == slug]
        return RuleCollection(
            rules=rules,
            warnings=list(self.warnings),
            errors=list(self.errors),
            root_path=self.root_path,
        )

    def list_rule_ids(self) -> list[str]:
        return [rule.id for rule in sorted(self.rules, key=lambda rule: rule.id)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_path": self.root_path,
            "rule_count": len(self.rules),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "rules": [
                rule.to_dict() for rule in sorted(self.rules, key=lambda rule: rule.id)
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=False)


class RuleCatalog:
    """Facade for grouped access to loaded enterprise rules."""

    def __init__(self, collection: RuleCollection):
        self.collection = collection

    @property
    def rules(self) -> list[Rule]:
        return self.collection.rules

    def group_by_category(self) -> dict[str, list[Rule]]:
        return self.collection.by_category()

    def group_by_applies_to(self) -> dict[str, list[Rule]]:
        return self.collection.by_applies_to()

    def category(self, category: str) -> RuleCollection:
        return self.collection.filter_category(category)


class RuleLoader:
    """Discover and load enterprise rule YAML files."""

    def __init__(self, root_path: str | Path | None = None):
        start = Path(root_path) if root_path else Path.cwd()
        self.root_path = ContextLoader.locate_root(start)
        self.rules_path = self.root_path / RULES_ROOT

    def load(self, *, category: str | None = None) -> RuleCollection:
        warnings: list[str] = []
        errors: list[str] = []
        rules: list[Rule] = []

        paths = self._discover_rule_files(category, warnings)
        for path in paths:
            rule = self._load_rule(path, warnings, errors)
            if rule is not None:
                rules.append(rule)

        return RuleCollection(
            rules=sorted(rules, key=lambda rule: rule.id),
            warnings=warnings,
            errors=errors,
            root_path=str(self.root_path),
        )

    def catalog(self) -> RuleCatalog:
        return RuleCatalog(self.load())

    def _discover_rule_files(
        self, category: str | None, warnings: list[str]
    ) -> list[Path]:
        if category:
            category_path = self.rules_path / _slug(category)
            if not category_path.is_dir():
                warnings.append(
                    f"Rule category folder was not found: {_display_path(category_path, self.root_path)}"
                )
                return []
            return sorted(category_path.glob("*.yaml"), key=lambda path: path.name)

        if not self.rules_path.is_dir():
            warnings.append(
                f"Rule catalog folder was not found: {_display_path(self.rules_path, self.root_path)}"
            )
            return []

        return sorted(self.rules_path.glob("*/*.yaml"), key=lambda path: path.as_posix())

    def _load_rule(
        self, path: Path, warnings: list[str], errors: list[str]
    ) -> Rule | None:
        display_path = _display_path(path, self.root_path)
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            logger.debug("Rule file is not valid YAML: %s", display_path, exc_info=True)
            errors.append(
                str(
                    RuleCatalogError(
                        f"Rule file is not valid YAML: {display_path}: {exc}"
                    )
                )
            )
            return None
        except OSError as exc:
            logger.debug("Rule file could not be read: %s", display_path, exc_info=True)
            errors.append(
                str(
                    RuleCatalogError(
                        f"Rule file could not be read: {display_path}: {exc}"
                    )
                )
            )
            return None

        if not isinstance(raw, dict):
            warnings.append(
                f"Rule file was skipped because it is not a mapping: {display_path}"
            )
            return None

        return Rule.from_mapping(raw, path=display_path)


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_string_value(item) for item in value if _string_value(item)]


def _bool_value(value: Any) -> bool:
    return value if isinstance(value, bool) else False


def _slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
