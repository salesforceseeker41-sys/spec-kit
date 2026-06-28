from __future__ import annotations

from pathlib import Path

from specify_cli.enterprise_context import ContextLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_config(root: Path, product_name: str = "rdra") -> None:
    _write(
        root / "enterprise.yaml",
        f"""
schema_version: "1.0"
enterprise:
  version: "1.0"
platform:
  name: "Enterprise Platform"
product:
  name: "{product_name}"
context:
  loadEnterprise: true
  loadProduct: true
""".lstrip(),
    )


def test_missing_enterprise_yaml_disables_loading_with_warning(tmp_path: Path) -> None:
    bundle = ContextLoader(tmp_path).load()

    assert not bundle.has_errors()
    assert bundle.config.exists is False
    assert bundle.config.load_enterprise is False
    assert bundle.config.load_product is False
    assert bundle.documents == []
    assert any("enterprise.yaml was not found" in warning for warning in bundle.warnings)


def test_valid_enterprise_yaml_loads_enterprise_and_product_docs(
    tmp_path: Path,
) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "enterprise/principles/security.md", "# Security\n")
    _write(tmp_path / "enterprise/salesforce/apex.md", "# Apex\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")

    bundle = ContextLoader(tmp_path).load()

    assert not bundle.has_errors()
    assert bundle.product_name == "rdra"
    assert bundle.list_loaded_paths() == [
        "enterprise/constitution.md",
        "enterprise/principles/security.md",
        "enterprise/salesforce/apex.md",
        "products/rdra/principles.md",
    ]


def test_missing_product_folder_warns_without_crashing(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")

    bundle = ContextLoader(tmp_path).load()

    assert not bundle.has_errors()
    assert bundle.list_loaded_paths() == ["enterprise/constitution.md"]
    assert any("Product context folder was not found" in warning for warning in bundle.warnings)


def test_feature_folder_loads_specification_md(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")
    _write(tmp_path / "specs/001-provider-program/specification.md", "# Feature Spec\n")

    bundle = ContextLoader(tmp_path).load("specs/001-provider-program")

    assert not bundle.has_errors()
    assert bundle.list_loaded_paths()[-1] == "specs/001-provider-program/specification.md"
    assert bundle.documents[-1].layer == "feature"
    assert bundle.documents[-1].category == "specification"


def test_feature_file_loads_directly(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")
    feature_file = tmp_path / "specs/001-provider-program/specification.md"
    _write(feature_file, "# Feature Spec\n")

    bundle = ContextLoader(tmp_path).load(feature_file)

    assert not bundle.has_errors()
    assert bundle.list_loaded_paths()[-1] == "specs/001-provider-program/specification.md"
    assert bundle.documents[-1].title == "Feature Spec"


def test_deterministic_ordering_is_stable(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "enterprise/principles/security.md", "# Security\n")
    _write(tmp_path / "enterprise/principles/architecture.md", "# Architecture\n")
    _write(tmp_path / "enterprise/salesforce/testing.md", "# Testing\n")
    _write(tmp_path / "enterprise/salesforce/apex.md", "# Apex\n")
    _write(tmp_path / "products/rdra/events.md", "# Events\n")
    _write(tmp_path / "products/rdra/domain-model.md", "# Domain Model\n")

    first = ContextLoader(tmp_path).load().list_loaded_paths()
    second = ContextLoader(tmp_path).load().list_loaded_paths()

    assert first == second
    assert first == [
        "enterprise/constitution.md",
        "enterprise/principles/architecture.md",
        "enterprise/principles/security.md",
        "enterprise/salesforce/apex.md",
        "enterprise/salesforce/testing.md",
        "products/rdra/domain-model.md",
        "products/rdra/events.md",
    ]
