from ortools.math_opt.python import mathopt

from units import Unit, build

# An island grid's diesel units, not the lesson's portfolio.
UNITS = [Unit("D1", 10, 40), Unit("D2", 25, 60), Unit("D3", 5, 20)]


def allowed(state: dict[str, tuple[int, float]], demand: float = 0) -> bool:
    """Fix every unit's on/off state and output, and ask SCIP whether the model accepts the hour."""
    model, on, power = build(UNITS, demand)
    for name, (is_on, mw) in state.items():
        on[name].lower_bound = on[name].upper_bound = is_on
        power[name].lower_bound = power[name].upper_bound = mw
    result = mathopt.solve(model, mathopt.SolverType.GSCIP)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_an_off_unit_makes_no_power():
    assert allowed({"D1": (0, 0), "D2": (0, 0), "D3": (0, 0)}) is True
    assert allowed({"D1": (0, 15), "D2": (0, 0), "D3": (0, 0)}) is False


def test_an_on_unit_runs_at_or_above_its_minimum():
    assert allowed({"D1": (1, 10), "D2": (0, 0), "D3": (1, 20)}) is True
    assert allowed({"D1": (1, 30), "D2": (0, 0), "D3": (0, 0)}, demand=30) is True
    assert allowed({"D1": (1, 4), "D2": (0, 0), "D3": (0, 0)}) is False


def test_each_unit_has_its_own_minimum():
    assert allowed({"D1": (0, 0), "D2": (1, 25), "D3": (0, 0)}) is True
    assert allowed({"D1": (0, 0), "D2": (1, 15), "D3": (0, 0)}) is False      # D1's minimum is 10
