"""Every snapshot passes its own tests and prints its expected report; every test a step adds fails
on the code before it, on an assertion; and the code before a step does not print its report."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import steps


@pytest.mark.parametrize("step", range(1, 7))
def test_the_step_passes_its_tests_and_its_new_tests_fail_before_it(step):
    after = steps.outcomes(step, step)
    assert after and all(o.result == "passed" for o in after), [o for o in after if o.result != "passed"]
    before = {o.test: o for o in steps.outcomes(step - 1, step)}
    for name in steps.new_or_changed(step):
        assert before[name].result == "failed" and before[name].kind == "AssertionError", before[name]
    kept = set(steps.test_sources(step)) - set(steps.new_or_changed(step))
    assert all(before[name].result == "passed" for name in kept)


def test_the_skeleton_passes_its_tests():
    assert all(o.result == "passed" for o in steps.outcomes(0, 0))


def report(root: Path) -> str:
    return subprocess.run([sys.executable, "main.py"], cwd=root, capture_output=True, text=True, timeout=300).stdout


@pytest.mark.parametrize("step", range(7))
def test_each_snapshot_prints_its_expected_report(step):
    expected = (steps.step_dir(step) / "expected" / "report.txt").read_text(encoding="utf-8")
    assert report(steps.step_dir(step)) == expected


@pytest.mark.parametrize("step", range(1, 7))
def test_the_code_before_a_step_does_not_print_its_report(step):
    expected = (steps.step_dir(step) / "expected" / "report.txt").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        assert report(steps.tree(step - 1, step, Path(tmp) / "project")) != expected
