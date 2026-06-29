"""Deterministic enterprise governance context loading.

This module is intentionally independent from Spec Kit command execution. It
discovers the enterprise governance scaffold, loads documents in a stable order,
and returns a structured bundle for future prompt builders and validators.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from .framework.exceptions import ConfigurationError

Layer = Literal["enterprise", "salesforce", "product", "feature"]
Category = Literal[
    "constitution",
    "principles",
    "standards",
    "integrations",
    "domain-model",
    "business-rules",
    "events",
    "specification",
    "other",
]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnterpriseConfig:
    """Normalized enterprise context loader configuration."""

    path: str | None
    exists: bool
    enterprise_version: str | None = None
    platform_name: str | None = None
    product_name: str | None = None
    load_enterprise: bool = False
    load_product: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "exists": self.exists,
            "enterprise_version": self.enterprise_version,
            "platform_name": self.platform_name,
            "product_name": self.product_name,
            "load_enterprise": self.load_enterprise,
            "load_product": self.load_product,
        }


@dataclass(frozen=True)
class ContextDocument:
    """One document discovered by the enterprise context loader."""

    path: str
    title: str
    category: Category
    layer: Layer
    required: bool
    exists: bool
    content: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self, *, include_content: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "path": self.path,
            "title": self.title,
            "category": self.category,
            "layer": self.layer,
            "required": self.required,
            "exists": self.exists,
            "warnings": list(self.warnings),
        }
        if include_content:
            payload["content"] = self.content
        return payload


@dataclass(frozen=True)
class ContextBundle:
    """Structured enterprise context returned by :class:`ContextLoader`."""

    config: EnterpriseConfig
    documents: list[ContextDocument]
    warnings: list[str]
    errors: list[str]
    root_path: str
    product_name: str | None = None
    feature_path: str | None = None

    def has_errors(self) -> bool:
        return bool(self.errors)

    def list_loaded_paths(self) -> list[str]:
        return [doc.path for doc in self.documents if doc.exists]

    def to_dict(self, *, include_content: bool = True) -> dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "documents": [
                doc.to_dict(include_content=include_content) for doc in self.documents
            ],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "root_path": self.root_path,
            "product_name": self.product_name,
            "feature_path": self.feature_path,
        }

    def to_json(self, *, include_content: bool = False, indent: int = 2) -> str:
        return json.dumps(
            self.to_dict(include_content=include_content),
            indent=indent,
            sort_keys=True,
        )

    def render_markdown(self) -> str:
        """Render deterministic markdown for human review and future prompts."""

        lines: list[str] = [
            "# Enterprise Context Bundle",
            "",
            f"- Root: `{self.root_path}`",
            f"- Product: `{self.product_name or 'none'}`",
            f"- Feature: `{self.feature_path or 'none'}`",
            "",
        ]

        if self.errors:
            lines.extend(["## Errors", ""])
            lines.extend(f"- {error}" for error in self.errors)
            lines.append("")

        if self.warnings:
            lines.extend(["## Warnings", ""])
            lines.extend(f"- {warning}" for warning in self.warnings)
            lines.append("")

        lines.extend(["## Documents", ""])
        if not self.documents:
            lines.extend(["No context documents were loaded.", ""])
            return "\n".join(lines).rstrip() + "\n"

        for doc in self.documents:
            status = "loaded" if doc.exists else "missing"
            lines.extend(
                [
                    f"### {doc.layer}: {doc.category}: {doc.title}",
                    "",
                    f"- Path: `{doc.path}`",
                    f"- Required: `{str(doc.required).lower()}`",
                    f"- Status: `{status}`",
                    "",
                ]
            )
            if doc.warnings:
                lines.extend(f"- Warning: {warning}" for warning in doc.warnings)
                lines.append("")
            if doc.content:
                lines.extend([doc.content.rstrip(), ""])

        return "\n".join(lines).rstrip() + "\n"


class ContextLoader:
    """Load enterprise governance context from a Spec Kit repository."""

    CONFIG_NAME = "enterprise.yaml"

    def __init__(self, root_path: str | Path | None = None):
        self.root_path = self.locate_root(Path(root_path) if root_path else Path.cwd())

    @classmethod
    def locate_root(cls, start: Path) -> Path:
        """Locate the repository root from *start*.

        Prefer an ancestor containing ``enterprise.yaml``. If no enterprise
        config exists, fall back to the nearest git root, then the resolved
        start directory. This keeps missing-config behavior graceful in tests
        and in repositories that have not adopted enterprise governance.
        """

        current = start.resolve()
        if current.is_file():
            current = current.parent

        for candidate in (current, *current.parents):
            if (candidate / cls.CONFIG_NAME).is_file():
                return candidate

        for candidate in (current, *current.parents):
            if (candidate / ".git").exists():
                return candidate

        return current

    def load(self, feature_path: str | Path | None = None) -> ContextBundle:
        warnings: list[str] = []
        errors: list[str] = []
        config = self._load_config(warnings, errors)
        documents: list[ContextDocument] = []

        if config.load_enterprise and not errors:
            documents.extend(self._load_enterprise_documents(warnings))
            documents.extend(self._load_salesforce_documents(warnings))

        if config.load_product and not errors:
            if config.product_name:
                documents.extend(self._load_product_documents(config.product_name, warnings))
            else:
                warnings.append(
                    "enterprise.yaml does not define product.name; product context was skipped."
                )

        resolved_feature = self._resolve_feature_path(feature_path, warnings)
        if resolved_feature is not None:
            documents.append(self._load_feature_document(resolved_feature))

        self._collect_document_warnings(documents, warnings)

        return ContextBundle(
            config=config,
            documents=documents,
            warnings=warnings,
            errors=errors,
            root_path=str(self.root_path),
            product_name=config.product_name,
            feature_path=str(resolved_feature) if resolved_feature else None,
        )

    def _load_config(
        self, warnings: list[str], errors: list[str]
    ) -> EnterpriseConfig:
        config_path = self.root_path / self.CONFIG_NAME
        if not config_path.is_file():
            warnings.append(
                "enterprise.yaml was not found; enterprise and product context loading are disabled."
            )
            return EnterpriseConfig(
                path=str(config_path),
                exists=False,
                load_enterprise=False,
                load_product=False,
            )

        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            logger.debug("enterprise.yaml is not valid YAML", exc_info=True)
            errors.append(
                str(ConfigurationError(f"enterprise.yaml is not valid YAML: {exc}"))
            )
            return EnterpriseConfig(path=str(config_path), exists=True)
        except OSError as exc:
            logger.debug("enterprise.yaml could not be read", exc_info=True)
            errors.append(
                str(ConfigurationError(f"enterprise.yaml could not be read: {exc}"))
            )
            return EnterpriseConfig(path=str(config_path), exists=True)

        if not isinstance(raw, dict):
            errors.append("enterprise.yaml is malformed: expected a YAML mapping.")
            return EnterpriseConfig(path=str(config_path), exists=True)

        enterprise = raw.get("enterprise")
        platform = raw.get("platform")
        product = raw.get("product")
        context = raw.get("context", {})

        if not isinstance(enterprise, dict):
            errors.append("enterprise.yaml is malformed: enterprise must be a mapping.")
            enterprise = {}
        if platform is not None and not isinstance(platform, dict):
            errors.append("enterprise.yaml is malformed: platform must be a mapping.")
            platform = {}
        if product is not None and not isinstance(product, dict):
            errors.append("enterprise.yaml is malformed: product must be a mapping.")
            product = {}
        if context is not None and not isinstance(context, dict):
            errors.append("enterprise.yaml is malformed: context must be a mapping.")
            context = {}

        enterprise_version = _string_value(enterprise.get("version"))
        platform_name = _string_value((platform or {}).get("name"))
        product_name = _string_value((product or {}).get("name"))

        if not enterprise_version:
            errors.append("enterprise.yaml is malformed: enterprise.version is required.")
        if not platform_name:
            errors.append("enterprise.yaml is malformed: platform.name is required.")
        if not product_name:
            warnings.append(
                "enterprise.yaml does not define product.name; product context will be skipped."
            )

        load_enterprise = _bool_value(context.get("loadEnterprise"), default=True)
        load_product = _bool_value(context.get("loadProduct"), default=True)

        return EnterpriseConfig(
            path=str(config_path),
            exists=True,
            enterprise_version=enterprise_version,
            platform_name=platform_name,
            product_name=product_name,
            load_enterprise=load_enterprise,
            load_product=load_product,
        )

    def _load_enterprise_documents(self, warnings: list[str]) -> list[ContextDocument]:
        docs = [
            self._load_context_document(
                self.root_path / "enterprise" / "constitution.md",
                layer="enterprise",
                category="constitution",
                required=True,
            )
        ]
        principles_dir = self.root_path / "enterprise" / "principles"
        docs.extend(
            self._load_folder_documents(
                principles_dir,
                layer="enterprise",
                category="principles",
                warnings=warnings,
            )
        )
        return docs

    def _load_salesforce_documents(self, warnings: list[str]) -> list[ContextDocument]:
        return self._load_folder_documents(
            self.root_path / "enterprise" / "salesforce",
            layer="salesforce",
            category="standards",
            warnings=warnings,
            recursive=True,
        )

    def _load_product_documents(
        self, product_name: str, warnings: list[str]
    ) -> list[ContextDocument]:
        product_dir = self.root_path / "products" / product_name
        if not product_dir.is_dir():
            warnings.append(
                f"Product context folder was not found: {product_dir.as_posix()}"
            )
            return []

        business_rules = product_dir / "business-rules.yaml"
        if not business_rules.is_file():
            warnings.append(
                f"Product business rules file was not found: {_display_path(business_rules, self.root_path)}"
            )

        supported = {
            path
            for pattern in ("*.md", "*.yaml", "*.yml")
            for path in product_dir.glob(pattern)
            if path.is_file()
        }
        return [
            self._load_context_document(
                path,
                layer="product",
                category=_category_from_name(path.stem),
                required=False,
            )
            for path in sorted(supported, key=_product_document_sort_key)
        ]

    def _load_folder_documents(
        self,
        folder: Path,
        *,
        layer: Layer,
        category: Category,
        warnings: list[str],
        recursive: bool = False,
    ) -> list[ContextDocument]:
        if not folder.is_dir():
            warnings.append(f"Context folder was not found: {folder.as_posix()}")
            return []
        paths = list(folder.rglob("*.md") if recursive else folder.glob("*.md"))
        if recursive and layer == "salesforce":
            paths.extend(folder.rglob("rules.yaml"))
        return [
            self._load_context_document(
                path, layer=layer, category=category, required=False
            )
            for path in sorted(
                set(paths), key=lambda item: item.relative_to(folder).as_posix()
            )
        ]

    def _resolve_feature_path(
        self, feature_path: str | Path | None, warnings: list[str]
    ) -> Path | None:
        if feature_path is None:
            return None

        path = Path(feature_path)
        if not path.is_absolute():
            path = self.root_path / path

        if path.exists() and path.is_dir():
            return path / "specification.md"
        if path.suffix:
            return path

        candidate = path / "specification.md"
        if not candidate.exists():
            warnings.append(
                f"Feature specification was not found: {candidate.as_posix()}"
            )
        return candidate

    def _load_feature_document(self, path: Path) -> ContextDocument:
        return self._load_context_document(
            path,
            layer="feature",
            category="specification",
            required=False,
        )

    def _load_context_document(
        self,
        path: Path,
        *,
        layer: Layer,
        category: Category,
        required: bool,
    ) -> ContextDocument:
        rel_path = _display_path(path, self.root_path)
        warnings: list[str] = []
        if not path.is_file():
            warnings.append(f"Document was not found: {rel_path}")
            return ContextDocument(
                path=rel_path,
                title=path.stem or rel_path,
                category=category,
                layer=layer,
                required=required,
                exists=False,
                warnings=warnings,
            )

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.debug(
                "Context document could not be read: %s", rel_path, exc_info=True
            )
            warnings.append(f"Document could not be read: {rel_path}: {exc}")
            return ContextDocument(
                path=rel_path,
                title=path.stem,
                category=category,
                layer=layer,
                required=required,
                exists=False,
                warnings=warnings,
            )

        return ContextDocument(
            path=rel_path,
            title=_extract_title(content, path.stem),
            category=category,
            layer=layer,
            required=required,
            exists=True,
            content=content,
            warnings=warnings,
        )

    @staticmethod
    def _collect_document_warnings(
        documents: list[ContextDocument], warnings: list[str]
    ) -> None:
        for doc in documents:
            warnings.extend(doc.warnings)


def _string_value(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _bool_value(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _category_from_name(name: str) -> Category:
    if name in {
        "constitution",
        "principles",
        "standards",
        "integrations",
        "domain-model",
        "business-rules",
        "events",
        "specification",
    }:
        return name  # type: ignore[return-value]
    return "other"


def _extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or fallback
    return fallback


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _product_document_sort_key(path: Path) -> tuple[int, str]:
    priority = {
        "principles.md": 0,
        "domain-model.md": 1,
        "business-rules.yaml": 2,
        "business-rules.yml": 2,
        "events.md": 3,
        "integrations.md": 4,
    }
    return (priority.get(path.name, 5), path.name)
