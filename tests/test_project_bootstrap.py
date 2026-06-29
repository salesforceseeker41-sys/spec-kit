"""Tests for optional Enterprise Spec Framework project bootstrap profiles."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from specify_cli import app
from specify_cli._assets import _locate_bundled_enterprise_root, _locate_bundled_profile
from specify_cli.bootstrap import install_profile


def _run_init(args: list[str]):
    runner = CliRunner()
    return runner.invoke(app, args)


ENTERPRISE_DOMAINS = {
    "security",
    "apex",
    "architecture",
    "flow",
    "lwc",
    "integration",
    "testing",
    "governance",
    "compliance",
    "devops",
    "observability",
    "deployment",
    "performance",
    "data",
    "monitoring",
}

DEPRECATED_TOP_LEVEL_ENTERPRISE_FOLDERS = {
    "apex",
    "architecture",
    "flow",
    "integration",
    "lwc",
    "salesforce-apex",
    "salesforce-architecture",
    "salesforce-flow",
    "salesforce-integration",
    "salesforce-security",
    "salesforce-testing",
    "security",
    "testing",
}


def _relative_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_init_without_profile_preserves_standard_behavior(tmp_path: Path) -> None:
    target = tmp_path / "plain-project"

    result = _run_init(
        [
            "init",
            str(target),
            "--integration",
            "codex",
            "--ignore-agent-tools",
            "--script",
            "sh",
        ]
    )

    assert result.exit_code == 0, result.output
    assert (target / ".agents" / "skills" / "speckit-plan" / "SKILL.md").exists()
    assert (target / ".specify" / "memory" / "constitution.md").exists()
    memory_constitution = (
        target / ".specify" / "memory" / "constitution.md"
    ).read_text(encoding="utf-8")
    assert "[PROJECT_NAME] Constitution" in memory_constitution
    assert "Enterprise Spec Framework Governance" not in memory_constitution
    assert not (target / "enterprise.yaml").exists()
    assert not (target / "enterprise").exists()
    assert not (target / "products").exists()


def test_salesforce_enterprise_profile_creates_bootstrap(tmp_path: Path) -> None:
    target = tmp_path / "enterprise-project"

    result = _run_init(
        [
            "init",
            str(target),
            "--integration",
            "codex",
            "--ignore-agent-tools",
            "--script",
            "sh",
            "--profile",
            "salesforce-enterprise",
        ]
    )

    assert result.exit_code == 0, result.output
    assert (target / ".agents" / "skills" / "speckit-plan" / "SKILL.md").exists()
    assert (target / "enterprise" / "constitution.md").exists()
    constitution = (target / "enterprise" / "constitution.md").read_text(
        encoding="utf-8"
    )
    assert "Enterprise Governance Constitution" in constitution
    assert "[PROJECT_NAME]" not in constitution
    assert "[PRINCIPLE_1_NAME]" not in constitution
    assert (target / "enterprise" / "principles" / "security.md").exists()
    assert (target / "enterprise" / "salesforce" / "apex.md").exists()
    assert (target / "enterprise" / "rules" / "security" / "SEC-001.yaml").exists()
    assert (target / "products" / "sample-product" / "principles.md").exists()
    assert (target / "products" / "sample-product" / "business-rules.yaml").exists()
    assert (target / "docs" / "esf-onboarding.md").exists()
    assert (target / "specs" / ".gitkeep").exists()

    enterprise_config = yaml.safe_load(
        (target / "enterprise.yaml").read_text(encoding="utf-8")
    )
    assert enterprise_config["platform"]["name"] == "Salesforce"
    assert enterprise_config["product"]["name"] == "sample-product"
    assert enterprise_config["context"]["loadEnterprise"] is True
    assert enterprise_config["context"]["loadProduct"] is True
    assert enterprise_config["governance"]["matcher"] == "keyword"

    profile_summary = json.loads(
        (target / ".specify" / "profile.json").read_text(encoding="utf-8")
    )
    assert profile_summary["profile"] == "salesforce-enterprise"
    assert profile_summary["source"] == "bundled"


def test_salesforce_enterprise_profile_writes_esf_memory_constitution(
    tmp_path: Path,
) -> None:
    target = tmp_path / "enterprise-project"

    result = _run_init(
        [
            "init",
            str(target),
            "--integration",
            "codex",
            "--ignore-agent-tools",
            "--script",
            "sh",
            "--profile",
            "salesforce-enterprise",
        ]
    )

    assert result.exit_code == 0, result.output
    content = (target / ".specify" / "memory" / "constitution.md").read_text(
        encoding="utf-8"
    )

    assert "Enterprise Spec Framework Governance" in content
    assert "This project follows Enterprise Spec Framework governance" in content
    assert "Platform Team owns `enterprise/` standards" in content
    assert "Product Team owns `products/sample-product/`" in content
    assert "enterprise.yaml" in content
    assert "ESF Context Loader" in content
    assert "enterprise/constitution.md" in content
    assert "enterprise/salesforce/**" in content
    assert "enterprise/rule-packs/**" in content
    assert "products/sample-product/**" in content
    assert "product:\n  name: sample-product" in content
    assert "Product teams must not edit enterprise standards" in content
    assert "Product teams may update their product folder" in content
    assert "[PROJECT_NAME]" not in content
    assert "[PRINCIPLE_1_NAME]" not in content
    assert "SFAPEX-101" not in content
    assert "APEX-001" not in content
    assert len(content) < 5000


def test_salesforce_enterprise_profile_copies_authoritative_enterprise_snapshot(
    tmp_path: Path,
) -> None:
    target = tmp_path / "enterprise-project"
    profile_path = _locate_bundled_profile("salesforce-enterprise")
    enterprise_root = _locate_bundled_enterprise_root()
    assert profile_path is not None
    assert enterprise_root is not None
    assert not (profile_path / "enterprise").exists()

    result = install_profile(target, profile_path, "salesforce-enterprise")

    expected_files = _relative_files(enterprise_root)
    actual_files = _relative_files(target / "enterprise")
    assert expected_files <= actual_files
    assert {
        path.name for path in (target / "enterprise").iterdir() if path.is_dir()
    }.isdisjoint(DEPRECATED_TOP_LEVEL_ENTERPRISE_FOLDERS)
    assert {
        path.parent.name
        for path in (target / "enterprise" / "rules").glob("*/*")
        if path.is_file()
    } >= ENTERPRISE_DOMAINS
    assert all(f"enterprise/{path}" in result.copied for path in expected_files)
    assert (target / "products" / "sample-product" / "principles.md").exists()
    assert (target / "products" / "sample-product" / "business-rules.yaml").exists()


def test_invalid_profile_gives_clear_error(tmp_path: Path) -> None:
    target = tmp_path / "bad-profile-project"

    result = _run_init(
        [
            "init",
            str(target),
            "--integration",
            "codex",
            "--ignore-agent-tools",
            "--script",
            "sh",
            "--profile",
            "unknown-profile",
        ]
    )

    assert result.exit_code == 1
    assert "Unknown profile: 'unknown-profile'" in result.output
    assert "salesforce-enterprise" in result.output
    assert not target.exists()


def test_profile_installer_preserves_existing_files_without_force(
    tmp_path: Path,
) -> None:
    target = tmp_path / "existing-project"
    target.mkdir()
    (target / ".specify").mkdir()
    (target / "enterprise.yaml").write_text("custom: true\n", encoding="utf-8")

    profile_path = _locate_bundled_profile("salesforce-enterprise")
    assert profile_path is not None

    result = install_profile(target, profile_path, "salesforce-enterprise")

    assert (target / "enterprise.yaml").read_text(encoding="utf-8") == "custom: true\n"
    assert "enterprise.yaml" in result.skipped
    assert (target / "enterprise" / "constitution.md").exists()
    assert (target / "products" / "sample-product" / "principles.md").exists()
    assert (target / "products" / "sample-product" / "business-rules.yaml").exists()
