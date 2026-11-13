"""Invariant: INV-1 — Every reading the API acknowledges with 2xx has a row in `reading`.
Fails when: the write handler returns before the insert commits, or catches an insert error and still answers 2xx.
Live from: the unit that builds app/readings/.

Structural check: the POST handler must call the repository's `insert` inside a transaction and
must not swallow exceptions. Green while app/readings/ does not exist.
"""
import ast
import pathlib

HANDLER = pathlib.Path("app/readings/router.py")


def test_inv_1_write_handler_commits_before_answering():
    if not HANDLER.exists():
        assert not HANDLER.parent.exists() or not list(HANDLER.parent.glob("*.py")), \
            "app/readings/ has code but no router.py: INV-1 cannot be checked"
        return
    tree = ast.parse(HANDLER.read_text())
    posts = [f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
             and any("post" in ast.unparse(d) for d in f.decorator_list)]
    assert posts, "no POST handler found in app/readings/router.py"
    for fn in posts:
        src = ast.unparse(fn)
        assert "transaction" in src, f"{fn.name}: the insert is not inside a transaction"
        for node in ast.walk(fn):
            if isinstance(node, ast.ExceptHandler):
                body = ast.unparse(node)
                assert "raise" in body, f"{fn.name}: an except block swallows the error and may still answer 2xx"
