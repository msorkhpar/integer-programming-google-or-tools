import pytest
from ortools.math_opt.python import mathopt

from direction import price_directions

# Stations: name -> (cost, value). Overtime: any amount up to its cap, worth RATE per unit.
STATIONS = {"north": (40, 60), "east": (30, 33), "south": (25, 36)}
RATE = 0.5


def solved(budget, cap):
    m = mathopt.Model()
    x = {s: m.add_binary_variable(name=s) for s in STATIONS}
    overtime = m.add_variable(lb=0, ub=cap, name="overtime")
    m.add_linear_constraint(sum(c * x[s] for s, (c, _) in STATIONS.items()) + overtime <= budget, name="budget")
    m.maximize(sum(v * x[s] for s, (_, v) in STATIONS.items()) + RATE * overtime)
    result = mathopt.solve(m, mathopt.SolverType.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    return m, result


def test_with_room_a_small_raise_gains_price_times_step():
    m, result = solved(budget=100, cap=20)      # all three stations (95), overtime 5 of 20
    answer = price_directions(m, result, "budget", 2)
    assert answer["price"] == pytest.approx(RATE)
    assert answer["up"] is True


def test_the_up_and_down_checks_each_start_from_the_original_limit():
    m, result = solved(budget=100, cap=20)
    answer = price_directions(m, result, "budget", 4)
    assert answer["up"] is True and answer["down"] is True
    row = next(r for r in m.linear_constraints() if r.name == "budget")
    assert row.upper_bound == pytest.approx(100)


def test_a_step_past_the_continuous_room_breaks_the_forecast():
    m, result = solved(budget=75, cap=20)       # north and south (65), overtime 10: room for 10 more, 10 less
    answer = price_directions(m, result, "budget", 18)
    assert answer["up"] is False and answer["down"] is False
    m, result = solved(budget=65, cap=20)       # north and south use it all: no overtime to cut
    answer = price_directions(m, result, "budget", 1)
    assert answer["up"] is True and answer["down"] is False


def test_the_price_comes_from_the_fixed_plan_not_the_relaxation():
    m, result = solved(budget=60, cap=20)       # east and south (55), overtime 5
    answer = price_directions(m, result, "budget", 2)
    assert answer["price"] == pytest.approx(RATE)
    assert answer["up"] is True and answer["down"] is True
