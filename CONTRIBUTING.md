# Contributing to Spec Kit

Hi there! We're thrilled that you'd like to contribute to Spec Kit. Contributions to this project are [released](https://help.github.com/articles/github-terms-of-service/#6-contributions-under-repository-license) to the public under the [project's open source license](LICENSE).

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Prerequisites for running and testing code

These are one time installations required to be able to test your changes locally as part of the pull request (PR) submission process.

1. Install [Python 3.11+](https://www.python.org/downloads/)
1. Install [uv](https://docs.astral.sh/uv/) for package management
1. Install [Git](https://git-scm.com/downloads)
1. Have an [AI coding agent available](README.md#-supported-ai-coding-agent-integrations)

<details>
<summary><b>💡 Hint if you are using <code>VSCode</code> or <code>GitHub Codespaces</code> as your IDE</b></summary>

<br>

Provided you have [Docker](https://docker.com) installed on your machine, you can leverage [Dev Containers](https://containers.dev) through this [VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), to easily set up your development environment, with aforementioned tools already installed and configured, thanks to the `.devcontainer/devcontainer.json` file (located at the root of the project).

To do so, simply:

- Checkout the repo
- Open it with VSCode
- Open the [Command Palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) and select "Dev Containers: Open Folder in Container..."

On [GitHub Codespaces](https://github.com/features/codespaces) it's even simpler, as it leverages the `.devcontainer/devcontainer.json` automatically upon opening the codespace.

</details>

## Submitting a pull request

> [!NOTE]
> If your pull request introduces a large change that materially impacts the work of the CLI or the rest of the repository (e.g., you're introducing new templates, arguments, or otherwise major changes), make sure that it was **discussed and agreed upon** by the project maintainers. Pull requests with large changes that did not have a prior conversation and agreement will be closed.

1. Fork and clone the repository
1. Configure and install the dependencies: `uv sync --extra test`
1. Make sure the CLI works on your machine: `uv run specify --help`
1. Create a new branch: `git checkout -b <type>/<number>-<short-slug>` (see [Branch naming](#branch-naming) below)
1. Make your change, add tests, and make sure everything still works
1. Test the CLI functionality with a sample project if relevant
1. Push to your fork and submit a pull request
1. Wait for your pull request to be reviewed and merged.

Activate the project virtual environment (see [Testing setup](#testing-setup) below), then install the CLI from your working tree (`uv pip install -e .` after `uv sync --extra test`) or otherwise ensure the shell uses the local `specify` binary before running the manual slash-command tests described below.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Follow the project's coding conventions.
- Write tests for new functionality.
- Update documentation (`README.md`, `spec-driven.md`) if your changes affect user-facing features.
- Keep your change as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests.
- Write a [good commit message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
- Test your changes with the Spec-Driven Development workflow to ensure compatibility.

## Enterprise Spec Framework contributions

The Enterprise Spec Framework (ESF) is an additive governance layer on top of Spec Kit for large Salesforce organizations. ESF contributions must preserve existing Spec Kit behavior unless a change is explicitly approved as a core Spec Kit change.

### ESF repository structure

| Path | Ownership | Contribution guidance |
| --- | --- | --- |
| `enterprise/` | Platform Team | Enterprise constitution, principles, Salesforce standards, and rule catalog. |
| `enterprise/rules/` | Platform Team | Machine-readable enterprise rules. Rules are data and must not require Python changes to edit policy. |
| `products/` | Product Teams | Product-domain standards, integrations, domain models, events, and future product rule packs. |
| `docs/enterprise-governance.md` | Platform Team | Operating model and ownership documentation. |
| `docs/context-loader.md` | Platform Team | Context Loader documentation. |
| `docs/governance-validation.md` | Platform Team | Advisory validation documentation. |
| `docs/rule-catalog.md` | Platform Team | Rule schema and catalog lifecycle documentation. |
| `ARCHITECTURE.md` | Platform Team | Authoritative ESF technical architecture. |
| `ROADMAP.md` | Platform Team | ESF version and sprint roadmap. |
| `DECISIONS.md` | Platform Team | Architecture Decision Records. |
| `scripts/load-enterprise-context.py` | Platform Team | Context inspection CLI. Keep behavior additive. |
| `scripts/validate-governance.py` | Platform Team | Advisory validation CLI. Do not introduce blocking behavior without an accepted ADR. |
| `scripts/load-rules.py` | Platform Team | Rule catalog inspection CLI. It must load and render rules only. |
| `src/specify_cli/enterprise_context.py` | Platform Team | Context Loader model and logic. |
| `src/specify_cli/governance_validation.py` | Platform Team | Advisory validation model and logic. |
| `src/specify_cli/rule_catalog.py` | Platform Team | Rule model and loader. |

### ESF branch strategy

Use the standard branch naming guidance in [Branch naming](#branch-naming). ESF documentation-only work should use `docs/`. ESF implementation work should use `feat/` unless it is a defect fix.

Examples:

```text
docs/esf-architecture-documentation
feat/esf-rule-engine
fix/esf-context-loader-warning
```

### ESF commit message convention

Use concise conventional-style messages:

```text
docs: add enterprise architecture documentation
feat: add enterprise rule catalog loader
fix: keep governance validation json output parseable
```

Every agent-authored commit must include the AI disclosure trailer required by this repository's agent disclosure policy.

### ESF code review process

ESF pull requests should answer:

- Does this preserve existing Spec Kit behavior?
- Is the change additive and backward compatible?
- Does the ownership model remain clear?
- Are enterprise rules represented as data rather than embedded policy?
- Are advisory and blocking behaviors clearly separated?
- Are docs, tests, and examples updated together?

### ESF coding standards

- Keep loaders separate from validators.
- Keep rule definitions out of Python.
- Prefer structured models over concatenated strings.
- Return warnings for missing optional governance files.
- Use errors only for malformed required inputs or runtime failures.
- Avoid command renames and workflow changes unless explicitly approved.
- Keep output deterministic for CI and multi-agent consumption.

### ESF documentation standards

Documentation should use consistent terminology:

- Enterprise Spec Framework or ESF.
- Platform Team.
- Product Teams.
- Delivery Teams.
- Context Loader.
- ContextBundle.
- Rule Catalog.
- Rule Pack.
- Governance Engine.
- Advisory Validation.

When adding or changing architecture, update the relevant document:

- Architecture: `ARCHITECTURE.md`.
- Roadmap: `ROADMAP.md`.
- Decisions: `DECISIONS.md`.
- User navigation: `README.md`.
- Operational details: `docs/*.md`.
- Release notes: `CHANGELOG.md`.

### How to add Enterprise Rules

1. Add one YAML file per rule under `enterprise/rules/<category>/`.
1. Use the rule ID as the filename, for example `SEC-006.yaml`.
1. Include every required field documented in `docs/rule-catalog.md`.
1. Set `owner: Platform Team`.
1. Use `severity: advisory` unless an accepted ADR defines another policy.
1. Run the rule catalog tests.

Enterprise rules are platform-owned. Delivery teams should not edit them inside feature work.

### How to add Product Rule Packs

Product rule packs are planned but not implemented yet. Until the structure is formalized:

1. Document proposed product-specific governance in `products/<product-id>/`.
1. Avoid adding product rules under `enterprise/rules/`.
1. Propose the product rule pack structure in an ADR before implementation.
1. Preserve enterprise-rule precedence.

### How to add Context Providers

Context providers are planned extension points. A new provider should:

- Return structured data.
- Preserve deterministic ordering.
- Avoid prompt-specific formatting in the provider.
- Degrade gracefully when optional files are missing.
- Include tests for missing, malformed, and ordered inputs.

### How to add Validators

Validators should:

- Consume `ContextBundle` and, after Sprint 4, `RuleCatalog` or `GovernanceEngine`.
- Produce structured findings and reports.
- Keep advisory behavior as the default.
- Avoid blocking delivery unless an accepted policy model enables it.
- Support deterministic text, markdown, and JSON output when exposed through a CLI.

### ESF testing expectations

For ESF changes, add or update focused tests:

- Context loading: `tests/test_enterprise_context_loader.py`.
- Governance validation: `tests/test_governance_validation.py`.
- Rule catalog: `tests/test_rule_catalog.py`.
- Existing Spec Kit compatibility: command package and console import smoke tests.

Recommended local checks:

```bash
.venv/bin/python -m pytest tests/test_enterprise_context_loader.py tests/test_governance_validation.py tests/test_rule_catalog.py -q
.venv/bin/python -m pytest tests/test_commands_package.py tests/test_console_imports.py -q
```

On Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_enterprise_context_loader.py tests\test_governance_validation.py tests\test_rule_catalog.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_commands_package.py tests\test_console_imports.py -q
```

### ESF release process

Document ESF changes in `CHANGELOG.md` under the Enterprise Spec Framework section. For release candidates and final releases, also update `VERSION`, `RELEASE_NOTES_v1.0.md`, `docs/compatibility.md`, and `docs/release-checklist.md` as needed. Include:

- Sprint or version placeholder.
- Added, Changed, Fixed, or Documentation entries.
- Any compatibility note.
- Any migration note.

Before tagging a release, complete the release checklist and run the focused ESF tests plus relevant Spec Kit smoke tests in a clean environment.

### Branch naming

We recommend naming branches as `<type>/<number>-<short-slug>`, where `<number>` is the issue or PR number (whichever comes first) and `<type>` is one of:

| Prefix | When to use | Example |
|---|---|---|
| `feat/` | New features | `feat/2342-workflow-cli-alignment` |
| `fix/` | Bug fixes | `fix/2653-paths-only-validation` |
| `docs/` | Documentation changes | `docs/2677-branch-naming-convention` |
| `community/` | Community catalog additions | `community/2492-add-mde-extension` |
| `chore/` | Maintenance, tooling, CI | `chore/2366-editorconfig` |

Including the issue or PR number makes branches traceable — especially useful since the project uses squash merges and `git branch --merged` won't detect merged branches. If you start with a PR (no issue), use the PR number once it's assigned.

## Development workflow

When working on spec-kit:

1. Test changes with the `specify` CLI commands (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`) in your coding agent of choice
2. Verify templates are working correctly in `templates/` directory
3. Test script functionality in the `scripts/` directory
4. Ensure memory files (`memory/constitution.md`) are updated if major process changes are made

### Recommended validation flow

For the smoothest review experience, validate changes in this order:

1. **Run focused automated checks first** — use the quick verification commands [below](#automated-checks) to catch scaffolding and configuration regressions early.
2. **Run manual workflow tests second** — if your change affects slash commands or the developer workflow, follow the [manual testing](#manual-testing) section to choose the right commands, run them in an agent, and capture results for your PR.

### Automated checks

#### Agent configuration and wiring consistency

```bash
uv run python -m pytest tests/test_agent_config_consistency.py -q
```

Run this when you change agent metadata, context update scripts, or integration wiring.

#### Running the full test suite

Install the test dependencies into the project's own virtual environment and run
`pytest` through that interpreter:

```bash
uv pip install -e ".[test]"
.venv/bin/python -m pytest tests -q   # Windows: .venv\Scripts\python -m pytest tests -q
```

> **Note:** prefer `.venv/bin/python -m pytest` over a bare `uv run pytest`.
> If another Spec Kit checkout has an editable (`-e`) install registered in a
> shared/global environment, `uv run pytest` can resolve `specify_cli` to that
> *other* worktree, turning it into a partial namespace package that fails to
> import newly added subpackages. Running through the project `.venv` resolves
> `specify_cli` to this checkout's `src/`. This matches the gotcha documented in
> `AGENTS.md` (Common Pitfalls).

#### Shell scripts

```bash
git ls-files -z -- '*.sh' | xargs -0 shellcheck --severity=error
```

The CI `lint.yml` `shellcheck` job currently reports and blocks only
error-severity findings. Warnings such as SC2155 are intentionally outside this
job until a follow-up cleanup tightens the threshold.

### Manual testing

#### Testing setup

```bash
# Install the project and test dependencies from your local branch
cd <spec-kit-repo>
uv sync --extra test
source .venv/bin/activate  # On Windows (CMD): .venv\Scripts\activate  |  (PowerShell): .venv\Scripts\Activate.ps1
uv pip install -e .
# Ensure the `specify` binary in this environment points at your working tree so the agent runs the branch you're testing.

# Initialize a test project using your local changes
uv run specify init <temp-dir>/speckit-test --integration <agent>
cd <temp-dir>/speckit-test

# Open in your agent
```

#### Manual testing process

Any change that affects a slash command's behavior requires manually testing that command through a coding agent and submitting results with the PR.

1. **Identify affected commands** — use the [prompt below](#determining-which-tests-to-run) to have your agent analyze your changed files and determine which commands need testing.
2. **Set up a test project** — scaffold from your local branch (see [Testing setup](#testing-setup)).
3. **Run each affected command** — invoke it in your agent, verify it completes successfully, and confirm it produces the expected output (files created, scripts executed, artifacts populated).
4. **Run prerequisites first** — commands that depend on earlier commands (e.g., `/speckit.tasks` requires `/speckit.plan` which requires `/speckit.specify`) must be run in order.
5. **Report results** — paste the [reporting template](#reporting-results) into your PR with pass/fail for each command tested.

#### Reporting results

Paste this into your PR:

~~~markdown
## Manual test results

**Agent**: [e.g., GitHub Copilot in VS Code]  |  **OS/Shell**: [e.g., macOS/zsh]

| Command tested | Notes |
|----------------|-------|
| `/speckit.command` | |
~~~

#### Determining which tests to run

Copy this prompt into your agent. Include the agent's response (selected tests plus a brief explanation of the mapping) in your PR.

~~~text
Read CONTRIBUTING.md, then run `git diff --name-only main` to get my changed files.
For each changed file, determine which slash commands it affects by reading
the command templates in templates/commands/ to understand what each command
invokes. Use these mapping rules:

- templates/commands/X.md → the command it defines
- scripts/bash/Y.sh or scripts/powershell/Y.ps1 → every command that invokes that script (grep templates/commands/ for the script name). Also check transitive dependencies: if the changed script is sourced by other scripts (e.g., common.sh is sourced by create-new-feature.sh, check-prerequisites.sh, setup-plan.sh), then every command invoking those downstream scripts is also affected
- templates/Z-template.md → every command that consumes that template during execution
- src/specify_cli/*.py → CLI commands (`specify init`, `specify check`, `specify extension *`, `specify preset *`); test the affected CLI command and, for init/scaffolding changes, at minimum test /speckit.specify
- extensions/X/commands/* → the extension command it defines
- extensions/X/scripts/* → every extension command that invokes that script
- extensions/X/extension.yml or config-template.yml → every command in that extension. Also check if the manifest defines hooks (look for `hooks:` entries like `before_specify`, `after_implement`, etc.) — if so, the core commands those hooks attach to are also affected
- presets/*/* → test preset scaffolding via `specify init` with the preset
- pyproject.toml → packaging/bundling; test `specify init` and verify bundled assets

Include prerequisite tests (e.g., T5 requires T3 requires T1).

Output in this format:

### Test selection reasoning

| Changed file | Affects | Test | Why |
|---|---|---|---|
| (path) | (command) | T# | (reason) |

### Required tests

Number each test sequentially (T1, T2, ...). List prerequisite tests first.

- T1: /speckit.command — (reason)
- T2: /speckit.command — (reason)
~~~

## AI contributions in Spec Kit

> [!IMPORTANT]
>
> If you are using **any kind of AI assistance** to contribute to Spec Kit,
> it must be disclosed in the pull request or issue.

We welcome and encourage the use of AI tools to help improve Spec Kit! Many valuable contributions have been enhanced with AI assistance for code generation, issue detection, and feature definition.

That being said, if you are using any kind of AI assistance (e.g., agents, ChatGPT) while contributing to Spec Kit,
**this must be disclosed in the pull request or issue**, along with the extent to which AI assistance was used (e.g., documentation comments vs. code generation).

If your PR responses or comments are being generated by an AI, disclose that as well.

As an exception, trivial spacing or typo fixes don't need to be disclosed, so long as the changes are limited to small parts of the code or short phrases.

An example disclosure:

> This PR was written primarily by GitHub Copilot.

Or a more detailed disclosure:

> I consulted ChatGPT to understand the codebase but the solution
> was fully authored manually by myself.

Failure to disclose this is first and foremost rude to the human operators on the other end of the pull request, but it also makes it difficult to
determine how much scrutiny to apply to the contribution.

In a perfect world, AI assistance would produce equal or higher quality work than any human. That isn't the world we live in today, and in most cases
where human supervision or expertise is not in the loop, it's generating code that cannot be reasonably maintained or evolved.

### What we're looking for

When submitting AI-assisted contributions, please ensure they include:

- **Clear disclosure of AI use** - You are transparent about AI use and degree to which you're using it for the contribution
- **Human understanding and testing** - You've personally tested the changes and understand what they do
- **Clear rationale** - You can explain why the change is needed and how it fits within Spec Kit's goals
- **Concrete evidence** - Include test cases, scenarios, or examples that demonstrate the improvement
- **Your own analysis** - Share your thoughts on the end-to-end developer experience

### What we'll close

We reserve the right to close contributions that appear to be:

- Untested changes submitted without verification
- Generic suggestions that don't address specific Spec Kit needs
- Bulk submissions that show no human review or understanding

### Guidelines for success

The key is demonstrating that you understand and have validated your proposed changes. If a maintainer can easily tell that a contribution was generated entirely by AI without human input or testing, it likely needs more work before submission.

Contributors who consistently submit low-effort AI-generated changes may be restricted from further contributions at the maintainers' discretion.

Please be respectful to maintainers and disclose AI assistance.

## Resources

- [Spec-Driven Development Methodology](./spec-driven.md)
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub Help](https://help.github.com)
