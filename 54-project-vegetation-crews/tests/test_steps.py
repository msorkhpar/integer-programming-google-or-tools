"""The project's snapshots and the lesson pages that quote them.

* every snapshot's own tests pass on its own code;
* every test a step adds fails against the snapshot before it, on an assertion (not an import,
  attribute or other error), so a project practice that starts from the before code fails until done;
* every python block a page quotes from a snapshot (marked `<!-- snapshot: steps/NN/path -->`) is
  lifted from that file, line by line in order, as scripts/verify_lessons.py checks blocks from src/.
"""

import re
import textwrap
from pathlib import Path

import pytest

from snapshots import STEPS, on_assertion, run_tests, ids_of_tests

MODULE = Path(__file__).resolve().parents[1]
MARK = re.compile(r"<!-- snapshot: (steps/\d\d/[\w/.]+) -->\n```python\n(.*?)^```", re.S | re.M)


@pytest.mark.parametrize("step", range(0, 9))
def test_each_snapshot_passes_its_own_tests(step):
    results = run_tests(step, step)
    assert results and all(outcome == "passed" for _, outcome, _ in results), results


@pytest.mark.parametrize("step", range(1, 9))
def test_every_added_test_fails_on_an_assertion_before_its_step(step):
    earlier = {name.split("::")[1] for name in ids_of_tests(step - 1)}
    added = {name for name in ids_of_tests(step) if name.split("::")[1] not in earlier}
    before = {name: (outcome, message) for name, outcome, message in run_tests(step - 1, step)}
    assert added
    for name in added:
        outcome, message = before.get(name, ("error", "not collected"))
        assert outcome == "failed" and on_assertion(message), (name, outcome, message)


def lines(text):
    return [line.strip() for line in textwrap.dedent(text).splitlines() if line.strip()]


def in_order(needle, hay):
    it = iter(hay)
    return all(any(line == h for h in it) for line in needle)


def test_every_quoted_block_is_lifted_from_its_snapshot():
    pages = sorted(MODULE.glob("README_14.1.*.md"))
    assert pages
    quoted = 0
    for page in pages:
        text = page.read_text()
        for match in MARK.finditer(text):
            source = MODULE / match.group(1)
            assert source.is_file(), (page.name, match.group(1))
            assert in_order(lines(match.group(2)), lines(source.read_text())), (page.name, match.group(1))
            quoted += 1
        # a python block is checked against src/ or its snapshot (verify_lessons), never skipped
        for block in re.finditer(r"^(.*)\n```python\n", text, re.M):
            assert block.group(1).strip() != "<!-- unverified -->", (page.name, block.start())
    assert quoted
