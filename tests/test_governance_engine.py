from __future__ import annotations

from specify_cli.enterprise_context import ContextBundle, ContextDocument, EnterpriseConfig
from specify_cli.framework.engine import ExecutionContext, GovernanceEngine
from specify_cli.framework.matchers import KeywordMatcher
from specify_cli.framework.reports import GovernanceFinding, GovernanceReport
from specify_cli.rule_catalog import Rule, RuleCatalog, RuleCollection


class FailingMatcher:
    def match(self, rule: Rule, document_content: str) -> object:
        raise RuntimeError("matcher unavailable")


def _rule(
    rule_id: str = "SEC-001",
    *,
    category: str = "Security",
    applies_to: list[str] | None = None,
    keywords: list[str] | None = None,
) -> Rule:
    return Rule(
        id=rule_id,
        title="CRUD/FLS Enforcement",
        category=category,
        description="All Apex operations must enforce CRUD and FLS.",
        rationale="Permission enforcement is required.",
        severity="advisory",
        default_enabled=True,
        applies_to=applies_to or ["specification"],
        keywords=keywords or ["CRUD", "FLS"],
        recommendation="Explicitly describe CRUD/FLS enforcement.",
        references=["Salesforce Secure Coding Guide"],
        owner="Platform Team",
        version="1.0",
        path=f"enterprise/rules/security/{rule_id}.yaml",
    )


def _bundle(*documents: ContextDocument) -> ContextBundle:
    return ContextBundle(
        config=EnterpriseConfig(
            path="enterprise.yaml",
            exists=True,
            enterprise_version="1.0",
            platform_name="Enterprise Platform",
            product_name="rdra",
            load_enterprise=True,
            load_product=True,
        ),
        documents=list(documents),
        warnings=[],
        errors=[],
        root_path="/repo",
        product_name="rdra",
        feature_path="specs/001-provider-program/specification.md",
    )


def _document(path: str, content: str) -> ContextDocument:
    return ContextDocument(
        path=path,
        title=path,
        category="other",
        layer="feature",
        required=False,
        exists=True,
        content=content,
    )


def _context(
    *,
    rules: list[Rule],
    documents: list[ContextDocument],
    artifact: str = "specification",
) -> ExecutionContext:
    return ExecutionContext(
        context_bundle=_bundle(*documents),
        rule_catalog=RuleCatalog(RuleCollection(rules=rules)),
        artifact=artifact,  # type: ignore[arg-type]
    )


def test_keyword_matcher_finds_keywords_case_insensitively() -> None:
    result = KeywordMatcher().match(
        _rule(keywords=["CRUD", "FLS"]),
        "The design covers crud and field access.",
    )

    assert result.matched
    assert result.matched_keywords == ["CRUD"]
    assert result.missing_keywords == ["FLS"]


def test_keyword_matcher_returns_missing_keywords_when_none_found() -> None:
    result = KeywordMatcher().match(
        _rule(keywords=["CRUD", "FLS"]),
        "The design covers business workflow only.",
    )

    assert not result.matched
    assert result.matched_keywords == []
    assert result.missing_keywords == ["CRUD", "FLS"]


def test_governance_engine_creates_no_finding_when_keyword_exists() -> None:
    context = _context(
        rules=[_rule()],
        documents=[
            _document(
                "specs/001-provider-program/specification.md",
                "Security requirements include CRUD/FLS enforcement.",
            )
        ],
    )

    report = GovernanceEngine().execute(context).report

    assert not report.has_findings()
    assert report.statistics.rules_passed == 1


def test_governance_engine_creates_advisory_finding_when_keyword_missing() -> None:
    context = _context(
        rules=[_rule()],
        documents=[
            _document(
                "specs/001-provider-program/specification.md",
                "Users can submit provider program requests.",
            )
        ],
    )

    report = GovernanceEngine().execute(context).report

    assert report.has_findings()
    assert report.findings[0].severity == "advisory"
    assert report.findings[0].rule_id == "SEC-001"
    assert report.findings[0].missing_keywords == ["CRUD", "FLS"]


def test_governance_engine_filters_rules_by_applies_to() -> None:
    context = _context(
        rules=[
            _rule("SEC-001", applies_to=["specification"]),
            _rule("TEST-001", category="Testing", applies_to=["tasks"]),
        ],
        documents=[
            _document(
                "specs/001-provider-program/specification.md",
                "Specification does not mention security keywords.",
            )
        ],
    )

    report = GovernanceEngine().execute(context).report

    assert report.statistics.rules_evaluated == 1
    assert [finding.rule_id for finding in report.findings] == ["SEC-001"]


def test_governance_report_groups_findings_by_category() -> None:
    report = GovernanceReport(
        feature_path="specs/001-provider-program",
        product_name="rdra",
        artifact="specification",
        findings=[
            GovernanceFinding(
                rule_id="SEC-001",
                rule_title="CRUD/FLS Enforcement",
                category="Security",
                severity="advisory",
                artifact="specification",
                message="Rule SEC-001 may not be addressed in specification.md.",
                recommendation="Add security coverage.",
                source_path="enterprise/rules/security/SEC-001.yaml",
                missing_keywords=["CRUD"],
            )
        ],
    )

    assert list(report.findings_by_category()) == ["Security"]


def test_governance_report_text_markdown_and_dict_rendering_work() -> None:
    context = _context(
        rules=[_rule()],
        documents=[_document("specs/001-provider-program/specification.md", "No keywords.")],
    )

    report = GovernanceEngine().execute(context).report

    assert report.to_dict()["findings"][0]["rule_id"] == "SEC-001"
    assert "Governance Validation Report" in report.to_text()
    assert "# Governance Validation Report" in report.to_markdown()


def test_missing_artifact_document_produces_warning_not_crash() -> None:
    context = _context(
        rules=[_rule(applies_to=["plan"])],
        documents=[],
        artifact="plan",
    )

    report = GovernanceEngine().execute(context).report

    assert not report.has_errors()
    assert any("No document was available for artifact: plan" in item for item in report.warnings)
    assert report.statistics.rules_evaluated == 0


def test_engine_propagates_rule_catalog_warnings_and_errors() -> None:
    context = ExecutionContext(
        context_bundle=_bundle(
            _document("specs/001-provider-program/specification.md", "No keywords.")
        ),
        rule_catalog=RuleCatalog(
            RuleCollection(
                rules=[],
                warnings=["Rule catalog folder was not found."],
                errors=["Rule file is not valid YAML."],
            )
        ),
        artifact="specification",
    )

    report = GovernanceEngine().execute(context).report

    assert "Rule catalog folder was not found." in report.warnings
    assert "Rule file is not valid YAML." in report.errors
    assert any("No governance rules were available" in item for item in report.warnings)


def test_matcher_runtime_failure_becomes_report_error() -> None:
    context = _context(
        rules=[_rule()],
        documents=[_document("specs/001-provider-program/specification.md", "No keywords.")],
    )

    report = GovernanceEngine(matcher=FailingMatcher()).execute(context).report

    assert report.has_errors()
    assert any("Rule matcher failed for SEC-001" in item for item in report.errors)
    assert not report.has_findings()
