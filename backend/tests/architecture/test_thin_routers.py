"""Routers must stay thin: parse -> one use case -> map. Business logic lives in use cases."""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "ups_kulka"
ROUTER_FILES = sorted((SRC / "modules").glob("*/presentation/*.py"))
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}

MAX_STATEMENTS = 3
FORBIDDEN_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith,
                   ast.Match, ast.Raise)
FORBIDDEN_NAMES = {"session", "AsyncSession", "select", "commit", "execute", "uow"}


def _endpoints(path: Path) -> list[ast.AsyncFunctionDef | ast.FunctionDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef):
            for deco in node.decorator_list:
                target = deco.func if isinstance(deco, ast.Call) else deco
                if isinstance(target, ast.Attribute) and target.attr in HTTP_METHODS:
                    result.append(node)
    return result


ENDPOINTS = [(path, fn) for path in ROUTER_FILES for fn in _endpoints(path)]


def test_routers_found() -> None:
    assert ENDPOINTS, "no router endpoints found; check the path in this test"


@pytest.mark.parametrize(("path", "fn"), ENDPOINTS, ids=lambda v: getattr(v, "name", v.name))
def test_endpoint_is_thin(path: Path, fn: ast.AsyncFunctionDef | ast.FunctionDef) -> None:
    where = f"{path.relative_to(SRC.parent)}::{fn.name}"
    body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]

    assert len(body) <= MAX_STATEMENTS, (
        f"{where}: {len(body)} statements; move logic into a use case (max {MAX_STATEMENTS})"
    )
    for node in ast.walk(fn):
        assert not isinstance(node, FORBIDDEN_NODES), (
            f"{where}:{node.lineno}: {type(node).__name__} in a router; "
            "branching, loops and error handling belong in use cases / global handlers"
        )
        if isinstance(node, ast.Name | ast.Attribute):
            name = node.id if isinstance(node, ast.Name) else node.attr
            assert name not in FORBIDDEN_NAMES, f"{where}: '{name}' — routers do not touch the DB"

    awaits = [n for n in ast.walk(fn) if isinstance(n, ast.Await)]
    assert len(awaits) <= 1, f"{where}: {len(awaits)} awaits; call exactly one use case"


@pytest.mark.parametrize(("path", "fn"), ENDPOINTS, ids=lambda v: getattr(v, "name", v.name))
def test_endpoint_gets_use_case_from_container(
    path: Path, fn: ast.AsyncFunctionDef | ast.FunctionDef
) -> None:
    source = ast.unparse(fn.args)
    assert "Provide[" in source, (
        f"{fn.name}: inject the use case with Depends(Provide['<module>.<use_case>'])"
    )
    decorators = {ast.unparse(d) for d in fn.decorator_list}
    assert "inject" in decorators, f"{fn.name}: missing @inject"
