"""Lesson 14.4.6: living specs, every scenario traced to a test and every test to a scenario.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/05, then steps/06.
"""

import shutil
import tempfile
from pathlib import Path

import changes
import steps


def show_trace(label, found):
    print(f"{label}: {found.pairs} scenarios with their tests")
    for item in found.untested:
        print(f"  no test: {item}")
    for item in found.untraced:
        print(f"  no scenario: {item}")


checker = changes.checker_module(6)
print("== trace, with the checker of steps/06")
show_trace("steps/05", checker.trace(steps.step_dir(5)))
open_tasks = [line.strip() for line in (changes.change_of(3) / "tasks.md").read_text(encoding="utf-8").splitlines()
              if line.strip().startswith("- [ ]")]
print(f"open tasks of {changes.change_of(3).name}:")
for line in open_tasks:
    print(f"  {line}")

steps.use(5)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import Project      # noqa: E402
from capplan.request import Request        # noqa: E402

LATE = [Project("A", "north", 600, 1000, 2027, 2029), Project("F", "north", 100, 150, 2030, 2030)]
request = Request(budget=1000, years=3, must_do={"F": "Regulator order RO-9"})
got = plan(LATE, request)
print(f"\nsteps/05, F must-do and may start only in 2030, plan 2027-2029: {len(got.starts)} started ({got.status})")
steps.use(6)
from capplan.plan import plan              # noqa: E402
from capplan.request import Request        # noqa: E402

try:
    plan(LATE, Request(budget=1000, years=3, must_do={"F": "Regulator order RO-9"}))
except ValueError as error:
    print(f"steps/06, the same request: refused, {error}")

print("\n== validate --strict, the change proposed")
changes.validate(6, 6)
print()
steps.show(6)

print("\n== trace, the change proposed and the tests of steps/06 written")
with tempfile.TemporaryDirectory() as tmp:
    root = changes.proposed(6, Path(tmp) / "project")
    shutil.rmtree(root / "tests")
    shutil.copytree(steps.step_dir(6) / "tests", root / "tests", ignore=steps.SKIP)
    show_trace("before archive", checker.trace(root))
    checker.archive(root, changes.change_id(6), changes.change_of(6).name[:10])
    show_trace("after archive", checker.trace(root))

print("\n== the archive and the living specs of steps/06")
for change in sorted((steps.step_dir(6) / "openspec" / "changes" / "archive").glob("*")):
    deltas = sorted(p.parent.name for p in change.glob("specs/*/spec.md"))
    print(f"  {change.name:44} {', '.join(deltas)}")
print("\n".join(checker.listing(steps.step_dir(6))))
