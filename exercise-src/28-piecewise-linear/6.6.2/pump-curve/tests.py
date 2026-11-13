from ortools.math_opt.python import mathopt

from booster import build

# A booster pump's curve, not the lesson's credit line. Slopes 1.5, 0.6, 1.4, 2.5.
XS, YS = (0, 20, 40, 60, 80), (0, 30, 42, 70, 120)


def allowed(flow: float, power: float, xs=XS, ys=YS) -> bool:
    """Fix the flow and the power, and ask whether the model accepts the pair."""
    model, q, p = build(xs, ys)
    q.lower_bound = q.upper_bound = flow
    p.lower_bound = p.upper_bound = power
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_points_on_the_curve_are_allowed():
    assert allowed(30, 36) is True          # 30 + 0.6 x 10
    assert allowed(50, 56) is True          # 42 + 1.4 x 10
    assert allowed(30, 50) is False         # above every mix of breakpoints at 30 (45)
    assert allowed(30, 20) is False         # below every mix of breakpoints at 30 (31.5)
    assert allowed(5, 20, (0, 10, 20), (0, 40, 50)) is True     # another curve: 40 x 5 / 10


def test_no_flow_past_the_last_breakpoint():
    assert allowed(80, 120) is True
    assert allowed(85, 130) is False


def test_no_point_between_the_curve_and_its_chords():
    assert allowed(30, 36) is True
    assert allowed(30, 33) is False         # the chord from 0 to 40 L/s passes 31.5
    assert allowed(30, 40) is False         # the chord from 0 to 80 L/s passes 45
