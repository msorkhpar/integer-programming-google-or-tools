"""What each step did to the planner's size and shape, measured from the snapshots.

Lines are the package's non-blank lines that are not comments; a function's branch count is
1 plus its decision points (if, for, while, comprehension, boolean operator, except), the
cyclomatic number of McCabe's measure; tests are the test functions of the snapshot.
"""

from __future__ import annotations

import ast
from pathlib import Path

STEPS = Path(__file__).resolve().parents[1] / "steps"
DECISIONS = (ast.If, ast.For, ast.While, ast.IfExp, ast.comprehension, ast.BoolOp, ast.ExceptHandler)


def lines(path: Path) -> int:
    return sum(1 for ln in path.read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.strip().startswith("#"))


def measure(step: int) -> dict:
    root = STEPS / f"{step:02d}"
    files = {p.name: lines(p) for p in sorted((root / "cipt").glob("*.py"))}
    functions = {}
    for path in sorted((root / "cipt").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef):
                functions[f"{path.stem}.{node.name}"] = 1 + sum(isinstance(n, DECISIONS) for n in ast.walk(node))
    tests = sum(ln.startswith("def test_") for p in (root / "tests").glob("test_*.py")
                for ln in p.read_text(encoding="utf-8").splitlines())
    worst = max(functions.items(), key=lambda kv: (kv[1], kv[0])) if functions else ("-", 0)
    return {"files": files, "lines": sum(files.values()), "functions": len(functions), "worst": worst,
            "tests": tests}


def show(step: int) -> None:
    before, after = measure(step - 1), measure(step)
    print(f"14.2.{step}: steps/{step - 1:02d} -> steps/{step:02d}")
    print(f"  package lines {before['lines']} -> {after['lines']}, functions {before['functions']} -> "
          f"{after['functions']}, tests {before['tests']} -> {after['tests']}")
    print(f"  most branches: {before['worst'][0]} ({before['worst'][1]}) -> {after['worst'][0]} ({after['worst'][1]})")
    for name in sorted(set(before["files"]) | set(after["files"])):
        a, b = before["files"].get(name, 0), after["files"].get(name, 0)
        if a != b:
            print(f"  {name:<12} {a:>4} -> {b:>4}")


if __name__ == "__main__":
    for n in range(1, 9):
        show(n)
