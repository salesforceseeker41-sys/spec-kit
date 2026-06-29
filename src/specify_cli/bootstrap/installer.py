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


def _profile_product_name(project_path: Path) -> str:
    config_path = project_path / "enterprise.yaml"
    if not config_path.is_file():
        return "sample-product"

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return "sample-product"

    if not isinstance(data, dict):
        return "sample-product"
    product = data.get("product")
    if not isinstance(product, dict):
        return "sample-product"
    name = product.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return "sample-product"


def _render_esf_memory_constitution(product_name: str) -> str:
    return f"""# ESF Project Constitution

## Enterprise Spec Framework Governance

This project follows Enterprise Spec Framework governance. This memory
constitution is the top-level Spec Kit governance pointer for `specify`, `plan`,
implementation, and test workflows. It does not duplicate the detailed
Enterprise Salesforce rule catalog.

## Runtime Governance Sources

All governed workflows must use the ESF Context Loader before generating or
changing specifications, plans, implementation tasks, implementation work, or
test guidance.

Load detailed governance from these runtime sources:

- Enterprise governance constitution: `enterprise/constitution.md`
- Enterprise Salesforce standards: `enterprise/salesforce/**`
- Enterprise Salesforce domain rules: `enterprise/salesforce/*/rules.yaml`
- Enterprise pack metadata: `enterprise/packs/**`
- Product governance: `products/{product_name}/**`
- Product selector and loader configuration: `enterprise.yaml`

The active product is selected by `enterprise.yaml`:

```yaml
product:
  name: {product_name}
```

## Ownership

- The Platform Team owns `enterprise/` standards, Salesforce standards, rule
  packs, and enterprise governance policy.
- The Product Team owns `products/{product_name}/` product principles, domain
  model, business rules, events, and integration context.
- Product teams must not edit enterprise standards or enterprise rule packs to
  solve product-specific issues without Platform Team approval.
- Product teams may update their product folder under
  `products/{product_name}/` as product knowledge changes.

## Workflow Requirements

- Use the ESF Context Loader for `specify`, `plan`, implementation, and test
  workflows.
- Treat `enterprise/` as the detailed Enterprise Governance source of truth.
- Treat `products/{product_name}/` as the detailed product governance source.
- Do not rely only on this memory constitution for governance decisions.
- Do not copy full enterprise rule content into this file; keep detailed rules
  in the enterprise governance hierarchy.
"""


def _write_esf_memory_constitution(
    project_path: Path,
    copied: list[str],
) -> None:
    product_name = _profile_product_name(project_path)
    memory_constitution = project_path / ".specify" / "memory" / "constitution.md"
    memory_constitution.parent.mkdir(parents=True, exist_ok=True)
    memory_constitution.write_text(
        _render_esf_memory_constitution(product_name),
        encoding="utf-8",
    )
    copied.append(".specify/memory/constitution.md")


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
        _write_esf_memory_constitution(project_path, copied)

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
