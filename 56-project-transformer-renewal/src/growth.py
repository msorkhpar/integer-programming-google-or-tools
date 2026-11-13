"""How the project grew, snapshot by snapshot: files, lines, functions, tests and branching.

Lines count code only (no blank lines, comments or docstrings). Branching is a McCabe-style count
for each function: 1, plus one for each if, for, while, comprehension condition, boolean operator,
except and conditional expression. The table shows the largest function's count and where it is.
"""

import ast
from pathlib import Path

import steps

BRANCHES = (ast.If, ast.For, ast.While, ast.IfExp, ast.ExceptHandler, ast.comprehension)


def code_lines(text: str) -> int:
    tree = ast.parse(text)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docstrings |= set(range(first.lineno, first.end_lineno + 1))
    return sum(1 for number, line in enumerate(text.splitlines(), start=1)
               if line.strip() and not line.strip().startswith("#") and number not in docstrings)


def branching(fn: ast.FunctionDef) -> int:
    count = 1
    for node in ast.walk(fn):
        if isinstance(node, BRANCHES):
            count += len(node.ifs) if isinstance(node, ast.comprehension) else 1
        elif isinstance(node, ast.BoolOp):
            count += len(node.values) - 1
    return count


def survey(step: int) -> dict:
    root = steps.step_dir(step)
    files = sorted((root / "renewal").glob("*.py"))
    functions = []
    for path in files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef):
                functions.append((branching(node), f"{path.stem}.{node.name}"))
    tests = len(steps.test_sources(step))
    return {"files": len(files), "lines": sum(code_lines(p.read_text(encoding="utf-8")) for p in files),
            "functions": len(functions), "tests": tests,
            "test_lines": sum(code_lines(p.read_text(encoding="utf-8")) for p in sorted((root / "tests").glob("*.py"))),
            "largest": max(functions)}


print("step  files  lines  functions  tests  test lines  most branching function")
for step in range(9):
    s = survey(step)
    print(f"{step:02d}    {s['files']:5}  {s['lines']:5}  {s['functions']:9}  {s['tests']:5}  {s['test_lines']:10}  "
          f"{s['largest'][1]} ({s['largest'][0]})")
