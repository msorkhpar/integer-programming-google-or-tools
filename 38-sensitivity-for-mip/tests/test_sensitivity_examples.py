"""The module 38 examples: no MILP duals, fixed-integer prices, the budget-value curve and its steps."""

import math

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import CLEARANCE_CAP, CLEARANCE_RATE, best_value, build, solve_glop, solve_highs


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_the_milp_has_no_duals_and_its_lp_relaxation_bounds_it_from_above(small):
    sel = build(small, small.capital_budget)
    result = solve_highs(sel.model)
    assert not result.has_dual_feasible_solution()
    with pytest.raises(ValueError):
        result.dual_values(sel.budget)
    lp = solve_glop(build(small, small.capital_budget, integer=False).model)
    assert lp.objective_value() > result.objective_value() + 1


def test_the_integer_value_function_is_superadditive_and_has_a_price_only_on_the_lp_line():
    import integer_dual as d
    z = d.value_function(d.D)
    assert all(z[a] + z[b] <= z[a + b] for a in range(d.D + 1) for b in range(d.D + 1 - a))
    for b in range(1, 22):
        up = max((z[e] - z[b]) / (e - b) for e in range(b + 1, d.D + 1))
        down = min((z[b] - z[e]) / (b - e) for e in range(b))
        assert (up <= down) == math.isclose(z[b], 10 * b / 7)


def test_dual_functions_bound_every_plan_and_a_bad_one_does_not():
    import integer_dual as d
    z = d.value_function(d.D)
    for name in ("value function z", "LP price 10d/7", "rounded LP floor(10d/7)"):
        F = d.candidates[name]
        assert d.is_dual_function(F) == []
        assert all(F(b) >= z[b] - 1e-9 for b in range(d.D + 1))
    assert d.is_dual_function(d.candidates["price 1.3d"])
    assert d.candidates["price 1.3d"](20) < z[20]


def test_the_fixed_lp_keeps_the_milp_value_and_prices_the_budget_at_the_clearance_rate(small):
    import fixed_duals
    sel, milp, lp = fixed_duals.fixed_lp(small.capital_budget)
    assert lp.objective_value() == pytest.approx(milp.objective_value())
    assert lp.dual_values(sel.budget) == pytest.approx(CLEARANCE_RATE)
    sel, milp, lp = fixed_duals.fixed_lp(66000)
    assert milp.variable_values(sel.clearance) == pytest.approx(CLEARANCE_CAP)
    assert lp.dual_values(sel.budget) == pytest.approx(0)


def test_inside_its_range_the_fixed_price_is_a_floor_on_the_milp_gain(small):
    import fixed_duals
    B = 38000
    sel, milp, _ = fixed_duals.fixed_lp(B)
    y = milp.variable_values(sel.clearance)
    for d in (-50, 10, 100, 500):
        assert -y <= d <= CLEARANCE_CAP - y
        gain = fixed_duals.milp_value(B + d) - milp.objective_value()
        assert gain >= CLEARANCE_RATE * d - 1e-6


def test_step_points_are_exact_against_a_10k_grid(small):
    from step_points import step_points
    assert all(p.capex % 10 == 0 for p in small.projects)          # so V can only step at multiples of 10
    points = step_points(small, 38000, 38300)
    steps = {b for b, _ in points[1:]}
    previous = best_value(small, 38000)
    for b in range(38010, 38301, 10):
        v = best_value(small, b)
        assert (v > previous) == (b in steps)
        previous = v
    assert [v for _, v in points] == [best_value(small, b) for b, _ in points]


def test_the_next_dollar_table_reads_gains_off_the_step_points(small):
    import next_dollar
    from step_points import step_points
    points = step_points(small, 38390, 39390)
    for d in (1, 20, 100, 1000):
        assert next_dollar.value_at(points, 38390 + d) == best_value(small, 38390 + d)


def test_pyomo_prices_the_plan_it_fixed(small):
    import pyomo.environ as pyo
    import pyomo_fixed
    m = pyomo_fixed.build(small.capital_budget)
    pyomo_fixed.highs(presolve=False).solve(m)
    assert pyo.value(m.npv) == pytest.approx(solve_highs(build(small, small.capital_budget, clearance=True).model)
                                             .objective_value())
    for v in m.x.values():
        v.fix(round(v.value))
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)
    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    pyomo_fixed.highs(presolve=False).solve(m)
    assert m.dual[m.budget] == pytest.approx(CLEARANCE_RATE)
