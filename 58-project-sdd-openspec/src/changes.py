"""Replay one step's OpenSpec change: propose it on the specs before the step, validate it, archive it.

Each snapshot keeps its changes archived, as OpenSpec leaves them. To show the step as it happened,
`proposed(NN)` copies snapshot NN-1 and puts snapshot NN's change back as an active change, the
state just before `archive`. `specs_check.py` is the project's own Python mirror of OpenSpec's
format rules, not the openspec CLI.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import steps


def change_of(step: int) -> Path:
    """The folder of the change the step archived: in steps/NN's archive, and not in steps/NN-1's."""
    def names(n):
        archive = steps.step_dir(n) / "openspec" / "changes" / "archive"
        return {p.name for p in archive.glob("*")} if archive.exists() else set()
    (new,) = names(step) - names(step - 1)
    return steps.step_dir(step) / "openspec" / "changes" / "archive" / new


def change_id(step: int) -> str:
    return change_of(step).name[len("2026-11-02-"):]


def proposed(step: int, into: Path) -> Path:
    """Snapshot NN-1, with snapshot NN's change active in openspec/changes/<id>."""
    shutil.copytree(steps.step_dir(step - 1), into, ignore=steps.SKIP)
    shutil.copytree(change_of(step), into / "openspec" / "changes" / change_id(step))
    return into


def validate(step: int, checker_step: int) -> None:
    """Print `specs_check.py validate --strict` of the proposed change, with one snapshot's checker."""
    checker = checker_module(checker_step)
    with tempfile.TemporaryDirectory() as tmp:
        root = proposed(step, Path(tmp) / "project")
        found = checker.validate(root)
        for item, issues in found.items():
            print(f"{'valid  ' if checker.passes(issues) else 'INVALID'} {item}")
            for issue in issues:
                print(f"  {issue}")
        print(f"strict: {sum(not checker.passes(i) for i in found.values())} item(s) failed")


def archive(step: int) -> None:
    """Archive the proposed change with the step's checker and compare the specs with snapshot NN's."""
    checker = checker_module(step)
    with tempfile.TemporaryDirectory() as tmp:
        root = proposed(step, Path(tmp) / "project")
        for note in checker.archive(root, change_id(step), change_of(step).name[:10]):
            print(note)
        for spec in sorted((steps.step_dir(step) / "openspec" / "specs").glob("*/spec.md")):
            rebuilt = root / "openspec" / "specs" / spec.parent.name / "spec.md"
            same = rebuilt.exists() and rebuilt.read_text(encoding="utf-8") == spec.read_text(encoding="utf-8")
            print(f"specs/{spec.parent.name}/spec.md after archive: {'the same as' if same else 'DIFFERS FROM'} "
                  f"steps/{step:02d}")


def planted(delta: str) -> list[tuple[str, str]]:
    """The capital-plan delta of step 01 with two faults planted, then a third, as lesson 14.4.1 shows."""
    faulty = (delta.replace("The planner SHALL start each project at most once in the plan.",
                            "The planner starts each project at most once in the plan.")
                   .replace("- **THEN** the plan's value equals the best value found by trying every plan\n", ""))
    worse = faulty.replace("""- **GIVEN** a project that may start in 2028 only, in a plan of 2027 to 2029
- **WHEN** a plan starts it in 2027, or in 2030
- **THEN** the plan is refused
- **AND** the plan that starts it in 2028 is allowed
""", "")
    assert delta != faulty != worse, "a fault was not planted"
    return [("two faults", faulty), ("three faults", worse)]


def checker_module(step: int):
    steps.use(step)
    import specs_check
    return specs_check


def listing(step: int) -> None:
    """Print `specs_check.py list` with the step's change proposed."""
    checker = checker_module(step)
    with tempfile.TemporaryDirectory() as tmp:
        print("\n".join(checker.listing(proposed(step, Path(tmp) / "project"))))
