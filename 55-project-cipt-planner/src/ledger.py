"""Each step's new tests, run against the code before the step and after it.

A step's practice starts from the snapshot before it (steps/NN-1) and is graded by the step's own
tests (steps/NN/tests). This program stages exactly that: the package of NN-1 with the tests of
NN, then the package of NN with its tests, and reports every test the step added. A new test must
fail on the old code on an assertion (a wrong answer), never on an import or attribute error, so
the learner starts from code that runs.

    python3 ledger.py          # every step
    python3 ledger.py 3        # step 14.2.3 only
"""

from __future__ import annotations

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
    test: str          # file::function
    kind: str          # "passed", "assertion" or the exception's type name
    line: str          # the first line of the failure message, or ""


def test_ids(step: int) -> list[str]:
    """Every test function of a snapshot, as file::function, read from the source."""
    found = []
    for path in sorted((STEPS / f"{step:02d}" / "tests").glob("test_*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("def test_"):
                found.append(f"{path.name}::{line[4:line.index('(')]}")
    return found


def run(code_step: int, test_step: int) -> dict[str, Outcome]:
    """Run the tests of `test_step` against the package (and data) of `code_step`."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for part in ("cipt", "data", "pytest.ini"):
            source = STEPS / f"{code_step:02d}" / part
            if source.is_dir():
                shutil.copytree(source, work / part)
            elif source.exists():
                shutil.copy(source, work / part)
        shutil.copytree(STEPS / f"{test_step:02d}" / "tests", work / "tests")
        subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        f"--junitxml={work / 'report.xml'}", "tests"],
                       cwd=work, capture_output=True, text=True, timeout=300)
        outcomes = {}
        for case in ET.parse(work / "report.xml").getroot().iter("testcase"):
            test = f"{case.get('classname').split('.')[-1]}.py::{case.get('name')}"
            bad = case.find("failure")
            if bad is None:
                bad = case.find("error")
            if bad is None:
                outcomes[test] = Outcome(test, "passed", "")
                continue
            message = (bad.get("message") or "").splitlines()[0].removeprefix("AssertionError: ")
            kind = "assertion" if message.startswith(("assert", "AssertionError", "Failed: DID NOT RAISE")) \
                else message.split(":")[0]
            outcomes[test] = Outcome(test, kind, message)
        return outcomes


def ledger(step: int) -> tuple[list[str], dict[str, Outcome], dict[str, Outcome]]:
    added = [t for t in test_ids(step) if t not in set(test_ids(step - 1))]
    return added, run(step - 1, step), run(step, step)


def show(step: int) -> None:
    added, before, after = ledger(step)
    on_old = sum(before[t].kind == "assertion" for t in added)
    passed = sum(o.kind == "passed" for o in after.values())
    print(f"14.2.{step}: {len(added)} tests added; on step {step - 1:02d}, {on_old} fail on an assertion; "
          f"on step {step:02d}, {passed} of {len(after)} pass")
    for t in added:
        line = before[t].line if before[t].kind == "assertion" else f"{before[t].kind}: {before[t].line}"
        print(f"  {t.split('::')[1]}")
        print(f"    before: {line[:88]}")
        print(f"    after:  {after[t].kind}")


if __name__ == "__main__":
    for n in ([int(a) for a in sys.argv[1:]] or [s for s in range(1, 9) if (STEPS / f"{s:02d}").is_dir()]):
        show(n)
