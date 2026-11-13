"""The project's snapshots, for the lesson programs: run one step's tests against another step's code,
import one step's package, and measure each step's code.

`steps/00` is the project before lesson 14.1.1 and `steps/NN` the project after lesson 14.1.NN. Each is
complete on its own: the `vegcrew` package, its tests and a pytest.ini.
"""

from __future__ import annotations

import ast
import importlib
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

STEPS = Path(__file__).resolve().parents[1] / "steps"


def step_dir(step: int) -> Path:
    return STEPS / f"{step:02d}"


def use(step: int):
    """Import the `vegcrew` package of one snapshot, forgetting any other snapshot's modules first."""
    for name in [m for m in sys.modules if m == "vegcrew" or m.startswith("vegcrew.")]:
        del sys.modules[name]
    sys.path[:] = [p for p in sys.path if not p.startswith(str(STEPS))]
    sys.path.insert(0, str(step_dir(step)))
    return importlib.import_module("vegcrew")


def run_tests(code: int, tests: int) -> list[tuple[str, str, str]]:
    """Run the tests of snapshot `tests` against the package of snapshot `code`, in a fresh process.

    Returns (test id, outcome, first line of the failure) per test; outcome is passed, failed or error.
    """
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "project"
        shutil.copytree(step_dir(code), work)
        shutil.rmtree(work / "tests")
        shutil.copytree(step_dir(tests) / "tests", work / "tests")
        report = Path(tmp) / "report.xml"
        subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={report}"],
                       cwd=work, capture_output=True, text=True)
        results = []
        for case in ET.parse(report).getroot().iter("testcase"):
            name = f"{case.get('classname').split('.')[-1]}::{case.get('name')}"
            outcome, message = "passed", ""
            for kind in ("failure", "error"):
                found = case.find(kind)
                if found is not None:
                    outcome = "failed" if kind == "failure" else "error"
                    message = (found.get("message") or "").splitlines()[0] if found.get("message") else ""
            results.append((name, outcome, message))
        return results


def ids_of_tests(step: int) -> set[str]:
    """Every test function of a snapshot, as file::name, read from the source.

    A test that moved to another file is the same test: `added` compares names only."""
    ids = set()
    for path in sorted((step_dir(step) / "tests").glob("test_*.py")):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                ids.add(f"{path.stem}::{node.name}")
    return ids


def on_assertion(message: str) -> bool:
    return message.startswith(("assert", "AssertionError"))


def print_before_after(step: int, width: int = 64) -> None:
    """The tests lesson 14.1.<step> adds, run against the code before the lesson and after it."""
    earlier = {name.split("::")[1] for name in ids_of_tests(step - 1)}
    added = {name for name in ids_of_tests(step) if name.split("::")[1] not in earlier}
    before = {name: (outcome, message) for name, outcome, message in run_tests(step - 1, step)}
    after = {name: (outcome, message) for name, outcome, message in run_tests(step, step)}
    print(f"tests added by lesson 14.1.{step}: {len(added)}")
    print(f"against steps/{step - 1:02d} (before):")
    for name in sorted(added):
        outcome, message = before.get(name, ("error", "not collected"))
        detail = f"  {message[:width]}" if message else ""
        print(f"  {outcome.upper():<6} {name}{detail}")
    kept = sorted(set(before) - added)
    print(f"  ...and {sum(before[n][0] == 'passed' for n in kept)} of {len(kept)} earlier tests pass")
    print(f"against steps/{step:02d} (after): {sum(o == 'passed' for o, _ in after.values())} of {len(after)} pass")


def size(step: int) -> dict[str, tuple[int, int]]:
    """Per file of the package: (lines of code, functions and methods), blank and comment lines left out."""
    out = {}
    for path in sorted((step_dir(step) / "vegcrew").glob("*.py")):
        text = path.read_text()
        code = [line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        funcs = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(ast.parse(text)))
        out[path.name] = (len(code), funcs)
    return out


def lines_of_tests(step: int) -> int:
    return sum(len([ln for ln in p.read_text().splitlines() if ln.strip()])
               for p in (step_dir(step) / "tests").glob("*.py"))


def print_sizes(before: int, after: int) -> None:
    """Lines of code and functions per package file, before and after a step, and the tests' lines."""
    old, new = size(before), size(after)
    print(f"code, steps/{before:02d} -> steps/{after:02d} (lines, functions; blanks and comments left out):")
    for name in sorted(set(old) | set(new)):
        a, b = old.get(name, (0, 0)), new.get(name, (0, 0))
        mark = "" if a == b else "  changed" if name in old and name in new else "  new" if name in new else "  gone"
        print(f"  {name:<12} {a[0]:>4} {a[1]:>3}  -> {b[0]:>4} {b[1]:>3}{mark}")
    total = [sum(v[i] for v in old.values()) for i in (0, 1)], [sum(v[i] for v in new.values()) for i in (0, 1)]
    print(f"  {'package':<12} {total[0][0]:>4} {total[0][1]:>3}  -> {total[1][0]:>4} {total[1][1]:>3}")
    print(f"  {'tests':<12} {lines_of_tests(before):>4} {len(ids_of_tests(before)):>3}  -> "
          f"{lines_of_tests(after):>4} {len(ids_of_tests(after)):>3}  (lines, tests)")


def solve_repeatably(planner, season, deterministic_time: float = 20.0):
    """Solve a snapshot's model (steps 04 to 06) the way lesson 4.6.3 makes a run repeat: one worker, a
    fixed seed and a limit on deterministic time. Returns the snapshot's own Plan and the solver."""
    from ortools.sat.python import cp_model

    tm = planner.build(season)
    for literal in getattr(tm, "rules", {}).values():
        tm.model.add(literal == 1)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = 7
    solver.parameters.max_deterministic_time = deterministic_time
    status = solver.status_name(solver.solve(tm.model))
    trims = {}
    for (cid, k), p in tm.present.items():
        if solver.boolean_value(p):
            start = solver.value(tm.start[cid, k])
            trims[cid] = planner.Trim(cid, k, start, start + season.circuit(cid).weeks)
    plan = planner.Plan(status, trims, cost=sum(season.circuit(t).cost for t in trims),
                        risk_carried=round(solver.objective_value))
    return plan, solver


def longest_function(step: int) -> tuple[str, int]:
    """The package's longest function or method, as file:name, and its length in lines."""
    best = ("", 0)
    for path in sorted((step_dir(step) / "vegcrew").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = node.end_lineno - node.lineno + 1
                if length > best[1]:
                    best = (f"{path.name}:{node.name}", length)
    return best
