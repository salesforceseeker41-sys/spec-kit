from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src" / "specify_cli"
ESF_MODULES = {
    "enterprise_context",
    "rule_catalog",
    "governance_validation",
    "framework",
}


def _module_name(path: Path) -> str:
    relative = path.relative_to(SRC_ROOT).with_suffix("")
    return ".".join(("specify_cli", *relative.parts))


def _esf_python_files() -> list[Path]:
    files = [
        SRC_ROOT / "enterprise_context.py",
        SRC_ROOT / "rule_catalog.py",
        SRC_ROOT / "governance_validation.py",
    ]
    files.extend((SRC_ROOT / "framework").rglob("*.py"))
    return sorted(files)


def _local_imports(path: Path, known_modules: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    module = _module_name(path)
    package = module.rsplit(".", 1)[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("specify_cli."):
                    imports.add(_nearest_known_module(alias.name, known_modules))
        elif isinstance(node, ast.ImportFrom):
            imported = _resolve_import_from(node, package)
            if imported and imported.startswith("specify_cli."):
                imports.add(_nearest_known_module(imported, known_modules))

    imports.discard("")
    imports.discard(module)
    return imports


def _resolve_import_from(node: ast.ImportFrom, package: str) -> str | None:
    if node.module is None:
        base = package
    elif node.level == 0:
        base = node.module
    else:
        parts = package.split(".")
        base_parts = parts[: len(parts) - node.level + 1]
        base = ".".join((*base_parts, node.module))

    if not base.startswith("specify_cli"):
        return None
    return base


def _nearest_known_module(imported: str, known_modules: set[str]) -> str:
    parts = imported.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in known_modules:
            return candidate
        parts.pop()
    return ""


def test_enterprise_framework_modules_have_no_circular_imports() -> None:
    known_modules = {_module_name(path) for path in _esf_python_files()}
    graph = {
        module: {
            dependency
            for dependency in _local_imports(path, known_modules)
            if dependency in known_modules
        }
        for path in _esf_python_files()
        for module in [_module_name(path)]
    }

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module: str, trail: tuple[str, ...]) -> None:
        assert module not in visiting, " -> ".join((*trail, module))
        if module in visited:
            return
        visiting.add(module)
        for dependency in graph[module]:
            visit(dependency, (*trail, module))
        visiting.remove(module)
        visited.add(module)

    for module in sorted(graph):
        visit(module, ())


def test_reports_layer_does_not_import_engine_layer() -> None:
    for path in (SRC_ROOT / "framework" / "reports").glob("*.py"):
        imports = _local_imports(path, {_module_name(item) for item in _esf_python_files()})
        assert not any(".framework.engine" in item for item in imports), path.as_posix()
