# Enterprise Spec Framework v1.0 Release Checklist

## Architecture

- [x] ESF remains additive to GitHub Spec Kit.
- [x] Context loading, rule loading, validation orchestration, engine execution, matching, and reporting have separate responsibilities.
- [x] Governance Engine does not depend on CLI argument parsing or terminal output.
- [x] Reports do not import the engine layer.
- [x] Circular dependency architecture test exists.

## Documentation

- [x] `README.md` includes Enterprise Governance navigation.
- [x] `ARCHITECTURE.md` documents component boundaries and public extension points.
- [x] `ROADMAP.md` documents v1.0 foundation and future phases.
- [x] `DECISIONS.md` records major architecture decisions.
- [x] `CHANGELOG.md` contains ESF release history.
- [x] `RELEASE_NOTES_v1.0.md` exists.
- [x] `docs/compatibility.md` exists.
- [x] `docs/release-checklist.md` exists.

## Tests

- [x] Context Loader tests exist.
- [x] Rule Catalog tests exist.
- [x] Governance Engine tests exist.
- [x] Governance Validator tests exist.
- [x] Architecture dependency tests exist.
- [x] Spec Kit command import smoke tests pass.
- [ ] Full repository test suite run in a fresh clone before tagging.
  - Current Windows note: upstream symlink and home-directory integration tests may require Developer Mode, elevated symlink privileges, or isolated agent home configuration.

## Performance

- [x] Current CLI use avoids unnecessary heavy dependencies.
- [x] Context and rule loading are deterministic.
- [ ] Long-lived cache strategy documented for future CI/editor integrations.
- [ ] Semantic matcher execution limits defined before implementation.

## Compatibility

- [x] Existing Spec Kit command names are unchanged.
- [x] Existing Spec Kit CLI behavior is unchanged.
- [x] Missing governance files warn instead of crashing where possible.
- [x] Validation remains advisory.
- [x] `ExecutionStatistics` backward-compatible import path is preserved.

## Security

- [x] Rule definitions are data, not executable code.
- [x] Governance scripts use repository-local files.
- [x] No telemetry is introduced.
- [x] No network dependency is introduced by ESF scripts.
- [ ] Platform Team rule wording reviewed for enterprise security policy alignment.

## Packaging

- [x] `VERSION` exists.
- [x] Release notes exist.
- [x] Compatibility matrix exists.
- [x] Changelog includes v1.0 release candidate notes.
- [ ] Fresh environment installation verified.
  - Include Windows PowerShell, Git Bash path handling, and non-Windows runner coverage before public release.

## Versioning

- [x] Version metadata is `1.0.0`.
- [x] ESF v1.0 scope is documented.
- [x] Known limitations are documented.
- [ ] Git tag `v1.0.0` created after final approval.

## Tagging

- [ ] Confirm working tree contains only intended release changes.
- [ ] Run final tests.
- [ ] Commit release candidate.
- [ ] Create annotated tag `v1.0.0`.
- [ ] Push branch and tag.

## Release Notes

- [x] Vision documented.
- [x] Major features documented.
- [x] Architecture documented.
- [x] Supported capabilities documented.
- [x] Known limitations documented.
- [x] Migration notes documented.
- [x] Future roadmap documented.

## Release Decision

Release status: approved with minor operational conditions.

Required before tagging:

1. Full test run in a clean environment.
2. Platform Team review of enterprise rules.
3. Final maintainer approval of release notes and compatibility matrix.
