"""Every snapshot passes its own tests, and every test a step adds fails on the snapshot before it
on an assertion (a wrong answer), never on an import or attribute error."""

import pytest

from ledger import ledger, run

STEPS = range(1, 9)


def test_skeleton_passes_its_own_tests():
    assert {o.kind for o in run(0, 0).values()} == {"passed"}


@pytest.mark.parametrize("step", STEPS)
def test_step_passes_and_its_new_tests_fail_before_it_on_assertions(step):
    added, before, after = ledger(step)
    assert added, f"step {step} adds no test"
    assert {o.kind for o in after.values()} == {"passed"}
    assert {t: before[t].kind for t in added} == {t: "assertion" for t in added}
