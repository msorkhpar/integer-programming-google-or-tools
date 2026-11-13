"""The openspec/ folder of every snapshot: it validates strictly, archiving its step's change onto the
snapshot before rebuilds its living specs exactly, and the trace finds only the one known gap."""

import tempfile
from pathlib import Path

import pytest

import changes
import steps

GAP = "capital-plan: A must-do that cannot start in the plan is refused"


@pytest.mark.parametrize("step", range(1, 7))
def test_every_snapshot_validates_strictly(step):
    checker = changes.checker_module(step)
    found = checker.validate(steps.step_dir(step))
    assert found and all(checker.passes(issues) for issues in found.values()), found


@pytest.mark.parametrize("step", range(1, 7))
def test_the_proposed_change_validates_strictly(step):
    checker = changes.checker_module(step)
    with tempfile.TemporaryDirectory() as tmp:
        found = checker.validate(changes.proposed(step, Path(tmp) / "project"))
    assert f"change {changes.change_id(step)}" in found
    assert all(checker.passes(issues) for issues in found.values()), found


@pytest.mark.parametrize("step", range(1, 7))
def test_archiving_the_change_rebuilds_the_living_specs(step):
    checker = changes.checker_module(step)
    with tempfile.TemporaryDirectory() as tmp:
        root = changes.proposed(step, Path(tmp) / "project")
        checker.archive(root, changes.change_id(step), changes.change_of(step).name[:10])
        rebuilt = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
                   for p in (root / "openspec").rglob("*.md")}
    kept = {p.relative_to(steps.step_dir(step)).as_posix(): p.read_text(encoding="utf-8")
            for p in (steps.step_dir(step) / "openspec").rglob("*.md")}
    assert rebuilt == kept


@pytest.mark.parametrize("step", range(1, 7))
def test_the_trace_finds_only_the_deferred_scenario(step):
    found = changes.checker_module(6).trace(steps.step_dir(step))
    assert found.untraced == []
    assert found.untested == ([GAP] if step in (3, 4, 5) else [])


def test_the_checker_refuses_what_the_lessons_plant():
    checker = changes.checker_module(6)
    living = (steps.step_dir(3) / "openspec" / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
    delta = (changes.change_of(4) / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
    assert checker.check_delta(delta, living, "d")[0] == []
    old_name = delta.replace("## MODIFIED Requirements\n\n### Requirement: Yearly budget with carry-over",
                             "## MODIFIED Requirements\n\n### Requirement: Yearly budget")
    assert [i.level for i in checker.check_delta(old_name, living, "d")[0]] == ["ERROR"]
    assert checker.check_delta("# notes only\n", None, "d")[0][0].message.startswith("no delta sections found")
    unpaired = "## RENAMED Requirements\n- FROM: `### Requirement: Yearly budget`\n"
    assert checker.check_delta(unpaired, living, "d")[0][0].message == "RENAMED FROM: Yearly budget has no partner line"
