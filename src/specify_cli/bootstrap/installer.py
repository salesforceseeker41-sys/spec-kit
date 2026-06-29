"""Install additive project bootstrap profiles."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .._assets import _locate_bundled_enterprise_root


@dataclass(frozen=True)
class BootstrapResult:
    """Summary of files copied or preserved during profile installation."""

    profile: str
    version: str
    copied: list[str]
    skipped: list[str]


def _relative_to_root(path: Path, root: Path) -> str:
    """Return a stable POSIX relative path and reject traversal."""
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    relative = resolved_path.relative_to(resolved_root)
    return relative.as_posix()


def _load_profile_metadata(profile_path: Path) -> dict[str, Any]:
    metadata_file = profile_path / "profile.yml"
    if not metadata_file.is_file():
        raise ValueError(f"Bootstrap profile metadata not found: {metadata_file}")

    try:
        data = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Bootstrap profile metadata is malformed: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Bootstrap profile metadata must be a YAML mapping")
    return data


def _copy_tree_files(
    *,
    source_root: Path,
    destination_root: Path,
    copied: list[str],
    skipped: list[str],
    force: bool,
    skip_relative_prefixes: tuple[str, ...] = (),
    output_prefix: str = "",
) -> None:
    for source in sorted(source_root.rglob("*")):
        if source.is_dir():
            continue

        relative = _relative_to_root(source, source_root)
        if relative in skip_relative_prefixes or any(
            relative.startswith(f"{prefix}/") for prefix in skip_relative_prefixes
        ):
            continue

        destination = destination_root / relative
        _relative_to_root(destination, destination_root)

        summary_path = f"{output_prefix}/{relative}" if output_prefix else relative

        if destination.exists() and not force:
            skipped.append(summary_path)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(summary_path)


def install_profile(
    project_path: Path,
    profile_path: Path,
    profile_id: str,
    *,
    force: bool = False,
) -> BootstrapResult:
    """Copy a bundled bootstrap profile into a project.

    Existing files are preserved unless ``force`` is true. The profile metadata
    file is not copied into the project; an installation summary is written to
    ``.specify/profile.json`` for traceability.
    """
    project_path = project_path.resolve()
    profile_path = profile_path.resolve()
    metadata = _load_profile_metadata(profile_path)
    version = str(metadata.get("version", "unknown"))

    copied: list[str] = []
    skipped: list[str] = []
    skip_profile_paths = ("profile.yml",)
    if profile_id == "salesforce-enterprise":
        skip_profile_paths = (*skip_profile_paths, "enterprise")

    _copy_tree_files(
        source_root=profile_path,
        destination_root=project_path,
        copied=copied,
        skipped=skipped,
        force=force,
        skip_relative_prefixes=skip_profile_paths,
    )

    if profile_id == "salesforce-enterprise":
        enterprise_root = _locate_bundled_enterprise_root()
        if enterprise_root is None:
            raise ValueError(
                "Bundled Enterprise Governance source was not found: enterprise/"
            )
        _copy_tree_files(
            source_root=enterprise_root,
            destination_root=project_path / "enterprise",
            copied=copied,
            skipped=skipped,
            force=force,
            output_prefix="enterprise",
        )

    profile_summary = {
        "profile": profile_id,
        "version": version,
        "source": "bundled",
        "copied_files": copied,
        "skipped_files": skipped,
    }
    summary_path = project_path / ".specify" / "profile.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(profile_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return BootstrapResult(
        profile=profile_id,
        version=version,
        copied=copied,
        skipped=skipped,
    )
