"""Every ```diff fence on a lesson page is lifted from the snapshots it names.

scripts/verify_lessons.py checks ```python fences against src/ only. The project's code lives in
steps/NN/, so the lessons show it as diffs between snapshots, and this test checks each hunk: its
old side (context and '-' lines) must appear, contiguous, in the old file, and its new side (context
and '+' lines) in the new file.
"""

import re
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1]
STEPS = MODULE / "steps"
FENCE = re.compile(r"^```diff\n(.*?)^```\s*$", re.S | re.M)


def fences():
    for page in sorted(MODULE.glob("README_*.md")):
        text = page.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            yield pytest.param(match.group(1), id=f"{page.name}:{text[:match.start()].count(chr(10)) + 1}")


def contiguous(needle, hay):
    n = len(needle)
    return n == 0 or any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def lines_of(path):
    return [] if path is None else [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.parametrize("body", list(fences()))
def test_the_diff_is_lifted_from_its_snapshots(body):
    lines = body.splitlines()
    assert lines[0].startswith("--- ") and lines[1].startswith("+++ "), "a diff names its two files"
    old_name, new_name = lines[0][4:].strip(), lines[1][4:].strip()
    old = lines_of(None if old_name == "/dev/null" else STEPS / old_name)
    new = lines_of(STEPS / new_name)
    hunk: list[str] = []
    for line in lines[2:] + ["@@"]:
        if line.startswith("@@"):
            before = [ln[1:].rstrip() for ln in hunk if ln[:1] in (" ", "-") or ln == ""]
            after = [ln[1:].rstrip() for ln in hunk if ln[:1] in (" ", "+") or ln == ""]
            assert contiguous(before, old), f"not in {old_name}: {before[:3]}"
            assert contiguous(after, new), f"not in {new_name}: {after[:3]}"
            hunk = []
        else:
            hunk.append(line)
