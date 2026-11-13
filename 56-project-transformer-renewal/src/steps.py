"""Run one snapshot's tests against another snapshot's code, and say what passed and failed.

The project lives in complete snapshots, `steps/NN/` (00 is the skeleton, NN the project after
lesson 14.3.NN). A step's practice starts from the code of snapshot NN-1 and is graded by the tests
of snapshot NN, so `outcomes(NN - 1, NN)` is what a learner sees on the first run.
"""

from __future__ import annotations

import importlib
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

STEPS = Path(__file__).resolve().parents[1] / "steps"


@dataclass(frozen=True)
class Outcome:
    test: str          # "test_plan.py::test_the_budget_..."
    result: str        # "passed", "failed" (an assertion or other exception in the test) or "error"
    kind: str          # the exception's type for a failure, "" otherwise
    message: str       # its first line


def step_dir(step: int) -> Path:
    return STEPS / f"{step:02d}"


def use(step: int):
    """Import the `renewal` package of one snapshot, dropping any other snapshot's modules first."""
    for name in [m for m in sys.modules if m == "renewal" or m.startswith("renewal.")]:
        del sys.modules[name]
    sys.path[:] = [p for p in sys.path if not p.startswith(str(STEPS))]
    sys.path.insert(0, str(step_dir(step)))
    importlib.invalidate_caches()
    return importlib.import_module("renewal")


def outcomes(code_step: int, tests_step: int) -> list[Outcome]:
    """Copy the package of `code_step` and the tests of `tests_step` together, run pytest, read its report."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "project"
        shutil.copytree(step_dir(code_step), work, ignore=shutil.ignore_patterns("tests", "__pycache__"))
        shutil.copytree(step_dir(tests_step) / "tests", work / "tests",
                        ignore=shutil.ignore_patterns("__pycache__"))
        report = Path(tmp) / "report.xml"
        subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={report}"],
                       cwd=work, capture_output=True, text=True, timeout=900)
        return read_report(report)


def read_report(report: Path) -> list[Outcome]:
    found = []
    for case in ET.parse(report).getroot().iter("testcase"):
        name = f"{case.get('classname', '').rsplit('.', 1)[-1]}.py::{case.get('name')}"
        failure, error = case.find("failure"), case.find("error")
        if failure is not None:
            message = (failure.get("message") or "").splitlines()[0] if failure.get("message") else ""
            raised = re.search(r"^E\s+(\w+(?:Error|Exception))\b", failure.text or "", re.M)
            kind = raised.group(1) if raised else "AssertionError"
            found.append(Outcome(name, "failed", kind, message))
        elif error is not None:
            found.append(Outcome(name, "error", "", (error.get("message") or "").splitlines()[0]))
        else:
            found.append(Outcome(name, "passed", "", ""))
    return found


def test_sources(step: int) -> dict[str, str]:
    """Each test function of a snapshot, by name, with its source text, to tell new tests from old."""
    import ast
    found = {}
    for path in sorted((step_dir(step) / "tests").glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        for node in ast.parse(text).body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                found[f"{path.name}::{node.name}"] = ast.get_source_segment(text, node)
    return found


def new_or_changed(step: int) -> list[str]:
    """The tests snapshot `step` adds, or changes, over snapshot `step - 1`."""
    before = test_sources(step - 1)
    return [name for name, source in test_sources(step).items() if before.get(name) != source]


def show(step: int) -> None:
    """Print what step's tests say about the code before the step and after it."""
    added = set(new_or_changed(step))
    for code, label in ((step - 1, "before"), (step, "after")):
        results = outcomes(code, step)
        passed = sum(o.result == "passed" for o in results)
        print(f"step {step:02d} tests on the code of step {code:02d} ({label}): "
              f"{passed} passed, {len(results) - passed} failed")
        for o in results:
            if o.result != "passed":
                print(f"  {o.result.upper():6} {o.test} ({o.kind or 'collection'})")
                print(f"         {o.message.removeprefix('AssertionError: ')[:96]}")
    print(f"tests step {step:02d} adds or changes: {len(added)}")
