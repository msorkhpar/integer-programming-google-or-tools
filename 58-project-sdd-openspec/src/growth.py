"""How the project grew, snapshot by snapshot: code, tests and specs.

Lines count code only (no blank lines, comments or docstrings), in capplan/ and specs_check.py.
Branching is a McCabe-style count for each function: 1, plus one for each if, for, while,
comprehension condition, boolean operator, except and conditional expression; the table shows the
largest. Requirements and scenarios are those of the living specs.
"""

import ast

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
    planner = sorted((root / "capplan").glob("*.py"))
    functions = []
    for path in planner:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef):
                functions.append((branching(node), f"{path.stem}.{node.name}"))
    checker = steps.use(step) and __import__("specs_check")
    reqs = [r for spec in sorted((root / "openspec" / "specs").glob("*/spec.md"))
            for r in checker.requirements(dict(checker.sections(spec.read_text(encoding="utf-8")))["Requirements"])]
    return {"planner": sum(code_lines(p.read_text(encoding="utf-8")) for p in planner),
            "checker": code_lines((root / "specs_check.py").read_text(encoding="utf-8")),
            "tests": len(steps.test_sources(step)), "requirements": len(reqs),
            "scenarios": sum(len(r.scenarios) for r in reqs), "largest": max(functions)}


print("step  planner lines  checker lines  tests  requirements  scenarios  most branching planner function")
for step in range(7):
    s = survey(step)
    print(f"{step:02d}    {s['planner']:13}  {s['checker']:13}  {s['tests']:5}  {s['requirements']:12}  "
          f"{s['scenarios']:9}  {s['largest'][1]} ({s['largest'][0]})")
