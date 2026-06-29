from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _template(name: str) -> str:
    return (REPO_ROOT / "templates" / "commands" / name).read_text(
        encoding="utf-8"
    )


def test_governed_prompts_describe_dynamic_product_context() -> None:
    for name in ("specify.md", "plan.md", "implement.md", "tasks.md"):
        content = _template(name)

        assert "Enterprise Context Loader" in content
        assert "enterprise/" in content
        assert "products/<product-name>/" in content
        assert "product-name` comes from `enterprise.yaml`" in content
        assert "business-rules.yaml" in content
        assert "Do not rely only on `.specify/memory/constitution.md`" in content
        assert "enterprise/salesforce/**/*.md" in content
        assert "enterprise/salesforce/*/rules.yaml" in content
        assert "Enterprise Salesforce Knowledge Pack" in content


def test_prompts_explain_runtime_product_loading() -> None:
    assert "next `/speckit-specify` run" in _template("specify.md")
    assert "next `/speckit-plan` run" in _template("plan.md")
    assert "next `/speckit-implement` run" in _template("implement.md")
