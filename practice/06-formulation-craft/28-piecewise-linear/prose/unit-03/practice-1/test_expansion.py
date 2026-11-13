from ortools.math_opt.python import mathopt

from expansion import build

WIDTHS = [4.0, 3.0, 5.0]          # ML/day added by each stage, not the lesson's credit line


def allowed(plan: list[float], widths=WIDTHS) -> bool:
    """Fix how much of each stage is built, and ask whether the model accepts the plan."""
    model, built = build(widths)
    for var, value in zip(built, plan):
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_stage_starts_only_after_the_one_before_is_finished():
    assert allowed([4.0, 1.5, 0.0]) is True
    assert allowed([0.5, 1.0, 0.0]) is False
    assert allowed([0.0, 0.0, 0.0]) is True


def test_a_later_stage_waits_for_every_earlier_one():
    assert allowed([4.0, 3.0, 2.0]) is True
    assert allowed([4.0, 0.0, 2.0]) is False
    assert allowed([0.3, 0.0, 0.0], [0.5, 2.0]) is True             # other widths: only the first begun


def test_a_stage_well_along_but_not_finished_holds_the_next():
    assert allowed([4.0, 0.0, 0.0]) is True
    assert allowed([2.0, 1.0, 0.0]) is False                        # 2 of stage 1's 4 ML/day
