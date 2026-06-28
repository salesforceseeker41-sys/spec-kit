"""Install additive project bootstrap profiles."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


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

    for source in sorted(profile_path.rglob("*")):
        if source.is_dir() or source.name == "profile.yml":
            continue

        relative = _relative_to_root(source, profile_path)
        destination = project_path / relative
        _relative_to_root(destination, project_path)

        if destination.exists() and not force:
            skipped.append(relative)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(relative)

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
