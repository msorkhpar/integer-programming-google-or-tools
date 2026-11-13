"""Every snapshot passes its own tests, and every test a step adds fails on the code before it,
on an assertion (the starter of the step's project practice imports cleanly)."""

import pytest

import steps

#: Tests a step changes (not adds) that still pass on the code before it, with the reason.
CHANGED_AND_PASSING: dict[tuple[int, str], str] = {}


@pytest.mark.parametrize("step", range(1, 9))
def test_the_step_passes_its_tests_and_its_new_tests_fail_before_it(step):
    after = steps.outcomes(step, step)
    assert after and all(o.result == "passed" for o in after), [o for o in after if o.result != "passed"]
    before = {o.test: o for o in steps.outcomes(step - 1, step)}
    for name in steps.new_or_changed(step):
        if (step, name) in CHANGED_AND_PASSING:
            continue
        assert before[name].result == "failed" and before[name].kind == "AssertionError", before[name]


def test_the_skeleton_passes_its_tests():
    assert all(o.result == "passed" for o in steps.outcomes(0, 0))
