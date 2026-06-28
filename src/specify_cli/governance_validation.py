"""Advisory enterprise governance validation orchestration.

Sprint 4B delegates governance evaluation to the reusable Governance Engine.
This module resolves feature artifacts and wires together the Context Loader,
Rule Catalog, ExecutionContext, and GovernanceEngine.
"""

from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path
from typing import Literal

from .enterprise_context import ContextBundle, ContextDocument, ContextLoader
from .framework.exceptions import ValidationError
from .framework.engine import ExecutionContext, GovernanceEngine
from .framework.reports import GovernanceReport
from .rule_catalog import RuleCatalog, RuleLoader

ArtifactName = Literal["spec", "specification", "plan", "tasks", "all"]
EngineArtifact = Literal["specification", "plan", "tasks", "all"]

ARTIFACT_FILES: dict[str, str] = {
    "specification": "specification.md",
    "plan": "plan.md",
    "tasks": "tasks.md",
}

logger = logging.getLogger(__name__)


class GovernanceValidator:
    """Orchestrate advisory governance validation through GovernanceEngine."""

    def __init__(
        self,
        root_path: str | Path | None = None,
        *,
        engine: GovernanceEngine | None = None,
    ):
        self.context_loader = ContextLoader(root_path)
        self.rule_loader = RuleLoader(self.context_loader.root_path)
        self.engine = engine or GovernanceEngine()
        self.root_path = self.context_loader.root_path

    def validate(
        self,
        feature_path: str | Path,
        artifact: ArtifactName = "all",
    ) -> GovernanceReport:
        try:
            return self._validate(feature_path, artifact)
        except Exception as exc:  # pragma: no cover - defensive CLI boundary
            logger.exception("Governance validation failed")
            return GovernanceReport(
                feature_path=str(feature_path),
                product_name=None,
                artifact=str(artifact),
                errors=[str(ValidationError(f"Governance validation failed: {exc}"))],
            )

    def _validate(
        self,
        feature_path: str | Path,
        artifact: ArtifactName,
    ) -> GovernanceReport:
        requested_artifact = _normalize_artifact(artifact)
        feature_dir = self._resolve_feature_dir(feature_path)
        warnings: list[str] = []
        documents: list[ContextDocument] = []

        if not feature_dir.exists() or not feature_dir.is_dir():
            warnings.append(
                f"Feature folder was not found: {_display_path(feature_dir, self.root_path)}"
            )

        artifacts_to_load = self._artifacts_to_load(
            feature_path,
            feature_dir,
            requested_artifact,
            warnings,
        )
        for artifact_name, path in artifacts_to_load:
            document = self._load_artifact_document(artifact_name, path, warnings)
            if document is not None:
                documents.append(document)

        if requested_artifact == "all" and not documents:
            warnings.append(
                f"No governance artifacts were found in {_display_path(feature_dir, self.root_path)}."
            )

        context_bundle = self._context_bundle_with_documents(documents, warnings)
        rule_collection = self.rule_loader.load()
        execution_context = ExecutionContext(
            context_bundle=context_bundle,
            rule_catalog=RuleCatalog(rule_collection),
            artifact=requested_artifact,
            feature_path=_display_path(feature_dir, self.root_path),
            product_name=context_bundle.product_name,
        )
        report = self.engine.execute(execution_context).report
        if artifact == "spec":
            return replace(report, artifact="spec")
        return report

    def _resolve_feature_dir(self, feature_path: str | Path) -> Path:
        path = Path(feature_path)
        if not path.is_absolute():
            path = self.root_path / path
        if path.suffix:
            return path.parent
        return path

    def _artifacts_to_load(
        self,
        feature_path: str | Path,
        feature_dir: Path,
        artifact: EngineArtifact,
        warnings: list[str],
    ) -> list[tuple[EngineArtifact, Path]]:
        if artifact == "all":
            return [
                (name, feature_dir / filename)
                for name, filename in ARTIFACT_FILES.items()
                if (feature_dir / filename).is_file()
            ]

        path = self._artifact_path(feature_path, feature_dir, artifact)
        if not path.is_file():
            warnings.append(
                f"Artifact '{_display_artifact(artifact)}' was not found: {_display_path(path, self.root_path)}"
            )
        return [(artifact, path)]

    def _artifact_path(
        self,
        feature_path: str | Path,
        feature_dir: Path,
        artifact: EngineArtifact,
    ) -> Path:
        path = Path(feature_path)
        if not path.is_absolute():
            path = self.root_path / path
        if artifact == "specification" and path.suffix:
            return path
        return feature_dir / ARTIFACT_FILES[artifact]

    def _load_artifact_document(
        self, artifact: EngineArtifact, path: Path, warnings: list[str]
    ) -> ContextDocument | None:
        if not path.is_file():
            return None

        rel_path = _display_path(path, self.root_path)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.debug("Could not read governance artifact %s", rel_path, exc_info=True)
            warnings.append(
                f"Artifact '{_display_artifact(artifact)}' could not be read: {rel_path}: {exc}"
            )
            return ContextDocument(
                path=rel_path,
                title=path.stem,
                category="other",
                layer="feature",
                required=False,
                exists=False,
                warnings=[f"Artifact '{_display_artifact(artifact)}' could not be read: {rel_path}"],
            )

        return ContextDocument(
            path=rel_path,
            title=path.stem,
            category="specification" if artifact == "specification" else "other",
            layer="feature",
            required=False,
            exists=True,
            content=content,
        )

    def _context_bundle_with_documents(
        self, documents: list[ContextDocument], warnings: list[str]
    ) -> ContextBundle:
        base_bundle = self.context_loader.load()
        return ContextBundle(
            config=base_bundle.config,
            documents=[*base_bundle.documents, *documents],
            warnings=[*base_bundle.warnings, *warnings],
            errors=list(base_bundle.errors),
            root_path=base_bundle.root_path,
            product_name=base_bundle.product_name,
            feature_path=documents[0].path if documents else None,
        )


def _normalize_artifact(artifact: ArtifactName) -> EngineArtifact:
    if artifact == "spec":
        return "specification"
    return artifact


def _display_artifact(artifact: str) -> str:
    if artifact == "specification":
        return "spec"
    return artifact


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
