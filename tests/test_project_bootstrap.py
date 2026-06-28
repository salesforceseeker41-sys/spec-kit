"""Tests for optional Enterprise Spec Framework project bootstrap profiles."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from specify_cli import app
from specify_cli._assets import _locate_bundled_profile
from specify_cli.bootstrap import install_profile


def _run_init(args: list[str]):
    runner = CliRunner()
    return runner.invoke(app, args)


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
    assert (target / "enterprise" / "principles" / "security.md").exists()
    assert (target / "enterprise" / "salesforce" / "apex.md").exists()
    assert (target / "enterprise" / "rules" / "security" / "SEC-001.yaml").exists()
    assert (target / "products" / "sample-product" / "principles.md").exists()
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
