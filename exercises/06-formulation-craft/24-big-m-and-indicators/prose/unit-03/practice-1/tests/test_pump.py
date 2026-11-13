from ortools.math_opt.python import mathopt

from pump import add_pump_rules, pump_variables

MIN_FLOW = 20


def allowed(flow_value: float, running: int) -> bool:
    model = mathopt.Model()
    flow, on = pump_variables(model)
    add_pump_rules(model, flow, on, MIN_FLOW)
    flow.lower_bound = flow.upper_bound = flow_value
    on.lower_bound = on.upper_bound = running
    result = mathopt.solve(model, mathopt.SolverType.GSCIP)       # SCIP takes indicator constraints
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_an_idle_pump_moves_nothing():
    assert allowed(0, running=0) is True
    assert allowed(5, running=0) is False


def test_a_running_pump_moves_at_least_the_minimum():
    assert allowed(20, running=1) is True
    assert allowed(10, running=1) is False


def test_a_running_pump_may_move_any_flow_above_the_minimum():
    assert allowed(100_000, running=1) is True
    assert allowed(100_000, running=0) is False
