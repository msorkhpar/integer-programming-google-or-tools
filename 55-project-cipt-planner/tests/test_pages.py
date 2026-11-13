"""Code a lesson quotes from a snapshot is in that snapshot's file.

A lesson fence quoting the project sits right after `<!-- snapshot: steps/NN/path -->`, which
scripts/verify_lessons.py follows to that file. This test checks the same thing inside the module's
own suite: every non-blank line of the fence, in order, in the snapshot file the marker names, and
the marker names the file the page's prose names last before the fence.
"""

import re
import textwrap
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"^```(\w+)[^\n]*\n(.*?)^```\s*$", re.S | re.M)
PATH = re.compile(r"steps/\d\d/[\w/]+\.(?:py|ini|json)")
SNAPSHOT = re.compile(r"<!-- snapshot: (steps/\d\d/[\w./-]+) -->")
LESSONS = sorted(MODULE.glob("README_*.md"))


def lines(text):
    return [ln.strip() for ln in textwrap.dedent(text).splitlines() if ln.strip()]


def in_order(needle, hay):
    it = iter(hay)
    return all(any(line == h for h in it) for line in needle)


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda p: p.name)
def test_snapshot_fences_are_lifted_from_the_named_file(lesson):
    text = lesson.read_text(encoding="utf-8")
    problems, last_end, seen = [], 0, 0
    for match in FENCE.finditer(text):
        before = text[last_end:match.start()]
        last_end = match.end()
        marker = SNAPSHOT.fullmatch((before.rstrip().splitlines() or [""])[-1].strip())
        if not marker:
            continue
        seen += 1
        line = text[:match.start()].count("\n") + 1
        quoted = marker.group(1)
        named = PATH.findall(text[:text.rfind(marker.group(0), 0, match.start())])
        if match.group(1) != "python" or not named or named[-1] != quoted:
            problems.append(f"{lesson.name}:{line}: a snapshot fence must be python and quote the file the prose names")
            continue
        source = (MODULE / quoted).read_text(encoding="utf-8")
        if not in_order(lines(match.group(2)), lines(source)):
            problems.append(f"{lesson.name}:{line}: not lifted from {quoted}")
    assert seen and not problems, problems
