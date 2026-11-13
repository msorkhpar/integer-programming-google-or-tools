from ortools.math_opt.python import mathopt

from setpoints import build

# A district heating network's setpoints, not the lesson's credit line.
TEMPS = [70, 75, 80, 85, 90, 95, 100, 105]
POWERS = [420, 360, 310, 300, 330, 390, 470, 560]


def allowed(temp: float, power: float, temps=TEMPS, powers=POWERS) -> bool:
    """Fix the temperature and the power, and ask whether the model accepts the pair."""
    model, t, p = build(temps, powers)
    t.lower_bound = t.upper_bound = temp
    p.lower_bound = p.upper_bound = power
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def binaries(temps, powers) -> int:
    model, _, _ = build(temps, powers)
    return sum(v.integer for v in model.variables())


def test_only_a_listed_setpoint_is_allowed():
    for temp, power in zip(TEMPS, POWERS):
        assert allowed(temp, power) is True
    assert allowed(85, 500) is False          # 85 °C with far more power than any setpoint near it
    assert allowed(87, 300) is False          # not a setpoint at all


def test_eight_setpoints_take_three_binaries():
    assert binaries(TEMPS, POWERS) <= 3
    assert allowed(70, 560) is False
    assert binaries([60, 65, 70], [500, 450, 480]) <= 2
    assert allowed(65, 450, [60, 65, 70], [500, 450, 480]) is True
    assert allowed(65, 495, [60, 65, 70], [500, 450, 480]) is False


def test_no_blend_of_two_setpoints():
    assert allowed(80, 310) is True
    assert allowed(82.5, 305) is False        # halfway between setpoints 2 and 3
    assert allowed(97.5, 430) is False        # halfway between setpoints 5 and 6
