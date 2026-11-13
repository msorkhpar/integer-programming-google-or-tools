"""Module 14.4: the real OpenSpec CLI, run on every snapshot's openspec/ folder and on every change.

The course's runner image carries Node.js and the OpenSpec CLI 2.0.0 (`openspec`, telemetry off).
This program runs it with subprocess, each command a fixed list of arguments and never a shell line,
always on a temporary copy, so the repository's own files never change:

* on each snapshot `steps/NN`: `openspec --version`, `openspec validate --all --strict`,
  `openspec list --specs` and `openspec list`;
* on each step's change, proposed on the snapshot before it (`changes.proposed`): the same validate
  and list, then `openspec archive <id> --yes`, and a comparison of the specs it writes with the
  living specs of `steps/NN`, which `specs_check.py archive` wrote;
* on lesson 14.4.1's planted faults (`changes.planted`): `openspec validate --all`, plain and strict.

Plain `openspec validate --strict` with no item and no terminal prints a hint and exits 1, so validation
always names `--all`. The CLI names the archive folder after the day it runs, so that date prints as
`<today>`, and the temporary folder's path as `<tmp>`. The portfolios are invented (GridCap is fictional).
"""

from __future__ import annotations

import datetime
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import changes
import steps

VERSION = ["openspec", "--version"]
VALIDATE = ["openspec", "validate", "--all", "--strict"]
VALIDATE_PLAIN = ["openspec", "validate", "--all"]
LIST_SPECS = ["openspec", "list", "--specs"]
LIST = ["openspec", "list"]
NO_ITEM = ["openspec", "validate", "--strict"]
ENV = {**os.environ, "NO_COLOR": "1", "FORCE_COLOR": "0", "DO_NOT_TRACK": "1", "OPENSPEC_TELEMETRY": "0"}


def run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run one fixed command in `cwd`: no shell, no terminal, no colour, no telemetry."""
    return subprocess.run(argv, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=120,
                          stdin=subprocess.DEVNULL)


def openspec(argv: list[str], cwd: Path) -> str:
    """Run one fixed command in `cwd`, and return what it printed with its exit status."""
    done = run(argv, cwd)
    text = (done.stdout + done.stderr).replace(str(cwd), "<tmp>")
    text = text.replace(datetime.date.today().isoformat(), "<today>")
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join([f"$ {' '.join(argv)}", *lines, f"(exit {done.returncode})"])


def fresh(root: Path) -> Path:
    """Stamp every file of a copy with the time now: `openspec list` prints how long ago a change changed."""
    for path in root.rglob("*"):
        os.utime(path)
    return root


def snapshot(step: int) -> None:
    """The CLI on a copy of steps/NN, whose changes are all archived."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "project"
        fresh(shutil.copytree(steps.step_dir(step), root, ignore=steps.SKIP))
        print(f"== steps/{step:02d}")
        for argv in (VALIDATE, LIST_SPECS, LIST):
            print(openspec(argv, root))


def change(step: int) -> None:
    """The CLI on steps/NN-1 with step NN's change active: validate, list, archive, compare."""
    name = changes.change_id(step)
    with tempfile.TemporaryDirectory() as tmp:
        root = fresh(changes.proposed(step, Path(tmp) / "project"))
        print(f"== {name}, proposed on steps/{step - 1:02d}")
        for argv in (VALIDATE, LIST):
            print(openspec(argv, root))
        print(f"-- specs_check.py list, the same folder, with the checker of steps/{step:02d}")
        print("\n".join(changes.checker_module(step).listing(root)))
        print(openspec(["openspec", "archive", name, "--yes"], root))
        for spec in sorted((steps.step_dir(step) / "openspec" / "specs").glob("*/spec.md")):
            rebuilt = root / "openspec" / "specs" / spec.parent.name / "spec.md"
            same = rebuilt.exists() and rebuilt.read_text(encoding="utf-8") == spec.read_text(encoding="utf-8")
            print(f"specs/{spec.parent.name}/spec.md after openspec archive: "
                  f"{'the same as' if same else 'DIFFERS FROM'} steps/{step:02d}")
        moved = sorted(p.name.replace(datetime.date.today().isoformat(), "<today>")
                       for p in (root / "openspec" / "changes" / "archive").glob(f"*-{name}"))
        print(f"archive folder: {', '.join(moved) or 'none'}")
        same = tree(root, changes.change_of(step).name[:10]) == tree(steps.step_dir(step))
        print(f"every file under openspec/, the archive's date set to steps/{step:02d}'s: "
              f"{'the same as' if same else 'DIFFERS FROM'} steps/{step:02d}")


def tree(root: Path, date: str | None = None) -> dict[str, bytes]:
    """Every file under root/openspec by its path, with today's date in a path read as `date`."""
    today = datetime.date.today().isoformat()
    return {(p.relative_to(root).as_posix().replace(today, date) if date else p.relative_to(root).as_posix()):
            p.read_bytes() for p in (root / "openspec").rglob("*") if p.is_file()}


def faults() -> None:
    """The CLI on lesson 14.4.1's planted faults: the baseline change, its capital-plan delta edited."""
    delta = changes.change_of(1) / "specs" / "capital-plan" / "spec.md"
    for label, text in changes.planted(delta.read_text(encoding="utf-8")):
        with tempfile.TemporaryDirectory() as tmp:
            root = fresh(changes.proposed(1, Path(tmp) / "project"))
            target = root / "openspec" / "changes" / changes.change_id(1) / "specs" / "capital-plan" / "spec.md"
            target.write_text(text, encoding="utf-8")
            print(f"== add-baseline-specs with {label}")
            for argv in (VALIDATE_PLAIN, VALIDATE):
                print(openspec(argv, root))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        print(openspec(VERSION, Path(tmp)))
    with tempfile.TemporaryDirectory() as tmp:
        root = fresh(shutil.copytree(steps.step_dir(6), Path(tmp) / "project", ignore=steps.SKIP))
        print("== steps/06, validate with no item and no --all")
        print(openspec(NO_ITEM, root))
    print()
    faults()
    for step in range(1, 7):
        print()
        change(step)
        print()
        snapshot(step)
