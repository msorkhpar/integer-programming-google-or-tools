"""The real OpenSpec CLI agrees with specs_check.py on every verdict and every archive the lessons show.

Runs in the course's runner image, which carries Node.js and `openspec` 2.0.0.
"""

import tempfile
from pathlib import Path

import pytest

import changes
import openspec_cli
import steps


@pytest.mark.parametrize("step", range(1, 7))
def test_the_cli_validates_and_archives_each_change_as_specs_check_did(step):
    checker = changes.checker_module(step)
    with tempfile.TemporaryDirectory() as tmp:
        root = changes.proposed(step, Path(tmp) / "project")
        assert all(checker.passes(issues) for issues in checker.validate(root).values())
        assert openspec_cli.run(openspec_cli.VALIDATE, root).returncode == 0
        done = openspec_cli.run(["openspec", "archive", changes.change_id(step), "--yes"], root)
        assert done.returncode == 0, done.stdout + done.stderr
        for spec in (steps.step_dir(step) / "openspec" / "specs").glob("*/spec.md"):
            rebuilt = root / "openspec" / "specs" / spec.parent.name / "spec.md"
            assert rebuilt.read_text(encoding="utf-8") == spec.read_text(encoding="utf-8")
        assert openspec_cli.tree(root, changes.change_of(step).name[:10]) == openspec_cli.tree(steps.step_dir(step))


def test_the_cli_and_the_checker_agree_on_the_planted_faults():
    checker = changes.checker_module(1)
    delta = changes.change_of(1) / "specs" / "capital-plan" / "spec.md"
    for label, text in changes.planted(delta.read_text(encoding="utf-8")):
        issues, _ = checker.check_delta(text, None, "d")
        with tempfile.TemporaryDirectory() as tmp:
            root = changes.proposed(1, Path(tmp) / "project")
            (root / "openspec" / "changes" / changes.change_id(1) / "specs" / "capital-plan" / "spec.md").write_text(
                text, encoding="utf-8")
            plain = openspec_cli.run(openspec_cli.VALIDATE_PLAIN, root).returncode == 0
            strict = openspec_cli.run(openspec_cli.VALIDATE, root).returncode == 0
        assert (plain, strict) == (checker.passes(issues, strict=False), checker.passes(issues)), label
