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


def test_product_context_includes_business_rules_yaml_in_defined_order(
    tmp_path: Path,
) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/rdra/integrations.md", "# Integrations\n")
    _write(tmp_path / "products/rdra/events.md", "# Events\n")
    _write(tmp_path / "products/rdra/domain-model.md", "# Domain Model\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")
    _write(
        tmp_path / "products/rdra/business-rules.yaml",
        "business_rules:\n  - id: BR-001\n    name: Eligibility\n",
    )
    _write(tmp_path / "products/rdra/z-extra.yml", "extra: true\n")
    _write(tmp_path / "products/rdra/a-extra.md", "# Extra\n")

    bundle = ContextLoader(tmp_path).load()

    assert not bundle.has_errors()
    assert bundle.list_loaded_paths() == [
        "enterprise/constitution.md",
        "products/rdra/principles.md",
        "products/rdra/domain-model.md",
        "products/rdra/business-rules.yaml",
        "products/rdra/events.md",
        "products/rdra/integrations.md",
        "products/rdra/a-extra.md",
        "products/rdra/z-extra.yml",
    ]
    business_doc = next(
        doc for doc in bundle.documents if doc.path == "products/rdra/business-rules.yaml"
    )
    assert business_doc.category == "business-rules"
    assert "BR-001" in business_doc.content


def test_context_loader_uses_product_name_from_enterprise_yaml(
    tmp_path: Path,
) -> None:
    _write_config(tmp_path, product_name="product-team1")
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")
    _write(tmp_path / "products/product-team1/principles.md", "# Team 1 Principles\n")
    _write(
        tmp_path / "products/product-team1/business-rules.yaml",
        "business_rules:\n  - id: BR-TEAM1\n    name: Team 1 Rule\n",
    )

    bundle = ContextLoader(tmp_path).load()

    assert bundle.product_name == "product-team1"
    assert "products/product-team1/principles.md" in bundle.list_loaded_paths()
    assert "products/product-team1/business-rules.yaml" in bundle.list_loaded_paths()
    assert "products/rdra/principles.md" not in bundle.list_loaded_paths()


def test_different_product_names_load_different_product_folders(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/alpha/principles.md", "# Alpha\n")
    _write(tmp_path / "products/beta/principles.md", "# Beta\n")

    _write_config(tmp_path, product_name="alpha")
    alpha = ContextLoader(tmp_path).load().list_loaded_paths()

    _write_config(tmp_path, product_name="beta")
    beta = ContextLoader(tmp_path).load().list_loaded_paths()

    assert "products/alpha/principles.md" in alpha
    assert "products/beta/principles.md" not in alpha
    assert "products/beta/principles.md" in beta
    assert "products/alpha/principles.md" not in beta


def test_missing_business_rules_warns_without_crashing(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "products/rdra/principles.md", "# RDRA Principles\n")

    bundle = ContextLoader(tmp_path).load()

    assert not bundle.has_errors()
    assert bundle.list_loaded_paths() == [
        "enterprise/constitution.md",
        "products/rdra/principles.md",
    ]
    assert any("Product business rules file was not found" in warning for warning in bundle.warnings)


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


def test_salesforce_context_loads_nested_runtime_documents(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Constitution\n")
    _write(tmp_path / "enterprise/salesforce/apex.md", "# Apex\n")
    _write(tmp_path / "enterprise/salesforce/security/sharing.md", "# Sharing\n")

    bundle = ContextLoader(tmp_path).load()

    assert bundle.list_loaded_paths() == [
        "enterprise/constitution.md",
        "enterprise/salesforce/apex.md",
        "enterprise/salesforce/security/sharing.md",
    ]


def test_loader_ignores_profile_enterprise_templates(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write(tmp_path / "enterprise/constitution.md", "# Runtime Constitution\n")
    _write(tmp_path / "enterprise/principles/security.md", "# Runtime Security\n")
    _write(
        tmp_path / "profiles/salesforce-enterprise/enterprise/constitution.md",
        "# Profile Constitution\n",
    )
    _write(
        tmp_path / "profiles/salesforce-enterprise/enterprise/principles/security.md",
        "# Profile Security\n",
    )

    bundle = ContextLoader(tmp_path).load()

    loaded = {doc.path: doc.content for doc in bundle.documents if doc.exists}
    assert loaded["enterprise/constitution.md"] == "# Runtime Constitution\n"
    assert loaded["enterprise/principles/security.md"] == "# Runtime Security\n"
    assert all(not path.startswith("profiles/") for path in loaded)
