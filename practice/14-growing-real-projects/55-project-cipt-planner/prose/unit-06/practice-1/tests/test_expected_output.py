"""The expected-output check, written by studyforge for this project. Read-only.

It runs the project's entry point and compares what it prints with the expected report: every
number within the tolerances below, every other character exactly.
"""

import difflib
import math
import re
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
ENTRY = 'main.py'
EXPECTED = 'expected/report.txt'
ABS_TOL = 0.05
REL_TOL = 0.0
NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _lines(text):
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _why(got, want):
    if NUMBER.split(got) != NUMBER.split(want):
        return "the text differs"
    for mine, theirs in zip(NUMBER.findall(got), NUMBER.findall(want)):
        if not math.isclose(float(mine), float(theirs), rel_tol=REL_TOL, abs_tol=ABS_TOL):
            return f"{mine} is not {theirs} within abs {ABS_TOL:g} or rel {REL_TOL:g}"
    return None


def test_the_report_matches_the_expected_output():
    try:
        done = subprocess.run(
            [sys.executable, str(WORKSPACE / ENTRY)],
            capture_output=True, text=True, timeout=120, check=False,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{ENTRY} printed no report within 120 seconds") from None
    assert done.returncode == 0, (
        f"{ENTRY} exited with {done.returncode} instead of printing a report:\n"
        + done.stderr[-3000:]
    )
    got = _lines(done.stdout)
    want = _lines((WORKSPACE / EXPECTED).read_text(encoding="utf-8"))
    problems = [
        f"line {number}: {why}"
        for number, (mine, theirs) in enumerate(zip(got, want), start=1)
        if (why := _why(mine, theirs)) is not None
    ]
    if len(got) != len(want):
        problems.append(f"the report has {len(got)} lines and the expected one {len(want)}")
    diff = difflib.unified_diff(want, got, "expected report", "your report", lineterm="")
    assert not problems, (
        f"{ENTRY} printed a report that differs from {EXPECTED}:\n"
        + "\n".join(problems[:10])
        + "\n\n"
        + "\n".join(diff)
    )
