"""Clean-architecture rules, checked on every test run.

Do NOT add exceptions here without an ADR in docs/adr/.
"""

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "ups_kulka"
MODULES_DIR = SRC / "modules"
LAYERS = ("domain", "application", "infrastructure", "presentation")

FRAMEWORKS = ("fastapi", "starlette", "sqlalchemy", "pydantic", "dependency_injector", "alembic")

# layer -> forbidden import prefixes (relative to the same module, plus frameworks)
FORBIDDEN_LAYERS: dict[str, tuple[str, ...]] = {
    "domain": ("application", "infrastructure", "presentation", "container"),
    "application": ("infrastructure", "presentation", "container"),
    "infrastructure": ("presentation", "container"),
    "presentation": ("infrastructure", "container", "domain"),
}
FORBIDDEN_FRAMEWORKS: dict[str, tuple[str, ...]] = {
    "domain": FRAMEWORKS,
    "application": FRAMEWORKS,
    "infrastructure": ("fastapi", "starlette", "dependency_injector"),
    "presentation": ("sqlalchemy", "alembic"),
}
# shared/<layer> follows the same rules as module layers.
SHARED_FORBIDDEN: dict[str, tuple[str, ...]] = {
    "domain": ("ups_kulka.shared.application", "ups_kulka.shared.infrastructure",
               "ups_kulka.shared.presentation", "ups_kulka.modules"),
    "application": ("ups_kulka.shared.infrastructure", "ups_kulka.shared.presentation",
                    "ups_kulka.modules"),
    "infrastructure": ("ups_kulka.shared.presentation", "ups_kulka.modules"),
    "presentation": ("ups_kulka.shared.infrastructure", "ups_kulka.modules"),
}


@dataclass(frozen=True)
class Import:
    file: Path
    line: int
    module: str


def _imports(path: Path) -> list[Import]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(Import(path, node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append(Import(path, node.lineno, node.module))
        elif isinstance(node, ast.ImportFrom) and node.level > 0:
            found.append(Import(path, node.lineno, "<relative>"))
    return found


def _module_layer_files() -> list[tuple[str, str, Path]]:
    files = []
    for module_dir in sorted(p for p in MODULES_DIR.iterdir() if p.is_dir()):
        if module_dir.name.startswith("__"):
            continue
        for layer in LAYERS:
            layer_dir = module_dir / layer
            files.extend((module_dir.name, layer, f) for f in layer_dir.rglob("*.py"))
    return files


def _rel(path: Path) -> str:
    return str(path.relative_to(SRC.parent))


MODULE_FILES = _module_layer_files()


def test_modules_have_all_layers() -> None:
    for module_dir in MODULES_DIR.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("__"):
            continue
        missing = [layer for layer in LAYERS if not (module_dir / layer).is_dir()]
        assert not missing, f"module '{module_dir.name}' is missing layers: {missing}"


def test_no_relative_imports() -> None:
    violations = [
        f"{_rel(imp.file)}:{imp.line}"
        for path in SRC.rglob("*.py")
        for imp in _imports(path)
        if imp.module == "<relative>"
    ]
    assert not violations, "use absolute imports only:\n" + "\n".join(violations)


@pytest.mark.parametrize(
    ("module", "layer", "path"),
    MODULE_FILES,
    ids=lambda v: _rel(v) if isinstance(v, Path) else str(v),
)
def test_layer_dependencies(module: str, layer: str, path: Path) -> None:
    own_prefix = f"ups_kulka.modules.{module}."
    violations: list[str] = []
    for imp in _imports(path):
        name = imp.module
        # 1. Direction of dependencies inside the module.
        for forbidden in FORBIDDEN_LAYERS[layer]:
            if name.startswith(own_prefix + forbidden):
                violations.append(f"{imp.line}: {layer} must not import {name}")
        # 2. Frameworks in pure layers.
        root = name.split(".")[0]
        if root in FORBIDDEN_FRAMEWORKS[layer]:
            violations.append(f"{imp.line}: {layer} must not depend on {root}")
        # 3. Other modules only through their application.public facade.
        if name.startswith("ups_kulka.modules.") and not name.startswith(own_prefix):
            other = name.split(".")[2]
            if not name.startswith(f"ups_kulka.modules.{other}.application.public"):
                violations.append(f"{imp.line}: cross-module import {name}; use .application.public")
        # 4. Nobody inside a module imports the composition root.
        if name in ("ups_kulka.container", "ups_kulka.main"):
            violations.append(f"{imp.line}: {layer} must not import {name}")
    assert not violations, f"{_rel(path)}\n" + "\n".join(violations)


@pytest.mark.parametrize("layer", list(SHARED_FORBIDDEN))
def test_shared_kernel_dependencies(layer: str) -> None:
    violations: list[str] = []
    for path in (SRC / "shared" / layer).rglob("*.py"):
        for imp in _imports(path):
            if any(imp.module.startswith(f) for f in SHARED_FORBIDDEN[layer]):
                violations.append(f"{_rel(path)}:{imp.line} imports {imp.module}")
            if imp.module.split(".")[0] in FORBIDDEN_FRAMEWORKS[layer]:
                violations.append(f"{_rel(path)}:{imp.line} depends on {imp.module}")
    assert not violations, "\n".join(violations)
