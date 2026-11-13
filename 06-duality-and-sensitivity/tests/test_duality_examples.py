"""The module 06 examples: the budget LP, its dual, complementary slackness, prices and their ranges."""

import math

import pytest
from ortools.math_opt.python import mathopt

from budget_lp import build, solve_glop
from certificates import plan_is_feasible, plan_value, price_bound, prices_are_feasible, reduced_cost, slack
from dualize import dualize
from gridcap import generate


@pytest.fixture(scope="module")
def tiny():
    return generate("tiny")


def test_the_one_year_lp_and_its_dual_meet_at_the_lesson_numbers():
    import one_year
    model, x = one_year.primal()
    primal = mathopt.solve(model, mathopt.SolverType.GLOP)
    dual_model, _ = one_year.dual()
    dual = mathopt.solve(dual_model, mathopt.SolverType.GLOP)
    assert primal.objective_value() == pytest.approx(1191.4)
    assert dual.objective_value() == pytest.approx(primal.objective_value())
    assert one_year.bound(0.43, 0.23, 0) == pytest.approx(1191.4)
    assert one_year.bound(0.43, 0, 0) is None


def test_dualize_gives_the_solvers_prices_with_the_right_signs(tiny):
    lp = build(tiny)
    dual_model, price = dualize(lp.model)
    primal = solve_glop(lp.model)
    dual = solve_glop(dual_model)
    assert dual.objective_value() == pytest.approx(primal.objective_value())
    for row in lp.model.linear_constraints():
        assert dual.variable_values(price[row.name]) == pytest.approx(primal.dual_values(row), abs=1e-9)
    assert primal.dual_values(lp.floor) < 0
    assert all(primal.dual_values(r) >= 0 for r in lp.cash.values())


def test_every_feasible_plan_is_below_every_feasible_price_bound(tiny):
    import weak_duality
    values = [plan_value(weak_duality.model, p) for p in weak_duality.plans.values()]
    assert all(plan_is_feasible(weak_duality.model, p) for p in weak_duality.plans.values())
    bounds = [b for b in map(lambda p: price_bound(weak_duality.model, p), weak_duality.price_systems.values())
              if b is not None]
    assert max(values) <= min(bounds) + 1e-6
    assert min(bounds) == pytest.approx(max(values))


def test_complementary_slackness_holds_at_the_optimum(tiny):
    lp = build(tiny)
    result = solve_glop(lp.model)
    plan = {v.name: result.variable_values(v) for v in lp.model.variables()}
    prices = {r.name: result.dual_values(r) for r in lp.model.linear_constraints()}
    assert prices_are_feasible(lp.model, prices)
    for row in lp.model.linear_constraints():
        assert slack(row, plan) * prices[row.name] == pytest.approx(0, abs=1e-6)
    for var in lp.model.variables():
        assert plan[var.name] * reduced_cost(lp.model, var, prices) == pytest.approx(0, abs=1e-6)
        assert reduced_cost(lp.model, var, prices) == pytest.approx(result.reduced_costs(var), abs=1e-9)


def test_cs_prices_certify_the_solvers_plan_and_refuse_the_early_floor_plan():
    import certify
    good = {v.name: certify.solver_plan.variable_values(v) for v in certify.model.variables()}
    assert prices_are_feasible(certify.model, certify.prices_from_plan(good))
    assert not prices_are_feasible(certify.model, certify.prices_from_plan(certify.worse))
    assert plan_is_feasible(certify.model, certify.worse)


def test_the_2028_price_holds_between_the_ranging_ends(tiny):
    def price(b):
        lp = build(tiny, budget={**tiny.budget, 2028: b})
        return solve_glop(lp.model).dual_values(lp.cash[2028])
    assert price(2990) == pytest.approx(price(8130)) == pytest.approx(price(3280))
    assert price(2970) > price(3280) > price(8150) > 0
    assert price(9750) == pytest.approx(0)


def test_highs_ranging_matches_the_re_solves(tiny):
    import highs_ranging
    rows = list(highs_ranging.lp.model.linear_constraints())
    i = rows.index(highs_ranging.lp.cash[2028])
    assert highs_ranging.ranging.row_bound_dn.value_[i] == pytest.approx(2980)
    assert highs_ranging.ranging.row_bound_up.value_[i] == pytest.approx(8140)


def test_a_reduced_cost_is_the_slope_of_forcing_an_idle_variable(tiny):
    lp = build(tiny, floor=None)
    result = solve_glop(lp.model)
    var = lp.spend["vegetation", 2027]
    rc = result.reduced_costs(var)
    lp.spend["vegetation", 2027].lower_bound = 100
    assert solve_glop(lp.model).objective_value() - result.objective_value() == pytest.approx(100 * rc)


def test_a_price_predicts_inside_its_range_and_overstates_beyond_it(tiny):
    lp = build(tiny)
    result = solve_glop(lp.model)
    price = result.dual_values(lp.cash[2028])
    for extra, exact in ((500, True), (6000, False)):
        more = solve_glop(build(tiny, budget={**tiny.budget, 2028: tiny.budget[2028] + extra}).model)
        gain = more.objective_value() - result.objective_value()
        assert (gain == pytest.approx(price * extra)) is exact
        assert gain <= price * extra + 1e-6


def test_the_milp_has_no_dual_values():
    import milp_has_no_prices as m
    with pytest.raises(ValueError):
        m.result.dual_values(m.row)
    assert not math.isnan(m.result.objective_value())


def test_a_minimization_prices_its_le_row_at_minus_two_in_both_or_tools_interfaces():
    from min_prices import with_mathopt, with_pywraplp
    value, x, price, reduced = with_mathopt()
    assert value == pytest.approx(-2) and x == [pytest.approx(1), pytest.approx(0)]
    assert price == pytest.approx(-2) and reduced == [pytest.approx(0), pytest.approx(1)]
    value, price, reduced = with_pywraplp()
    assert value == pytest.approx(-2) and price == pytest.approx(-2) and reduced == [pytest.approx(0), pytest.approx(1)]


def test_the_or_tools_advanced_sample_reports_prices_reduced_costs_and_the_basis():
    from or_tools_duals import model, rows, x
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    assert result.has_dual_feasible_solution() and result.has_basis()
    assert result.dual_values(rows) == [pytest.approx(2 / 3), pytest.approx(0, abs=1e-9), pytest.approx(10 / 3)]
    assert result.reduced_costs(x) == [pytest.approx(0, abs=1e-9), pytest.approx(0, abs=1e-9), pytest.approx(-8 / 3)]
    basic = mathopt.BasisStatus.BASIC
    assert [result.constraint_status(r) == basic for r in rows] == [False, True, False]
    assert [result.variable_status(v) == basic for v in x] == [True, True, False]


def test_lowering_2027_vegetation_value_keeps_the_plan_and_moves_only_the_floor_price(tiny):
    for coefficient in (0.31, -1.0, -100.0):
        lp = build(tiny)
        lp.model.objective.set_linear_coefficient(lp.spend["vegetation", 2027], coefficient)
        result = solve_glop(lp.model)
        assert [result.variable_values(lp.spend["vegetation", y]) for y in (2027, 2028, 2029)] == \
            pytest.approx([220, 340, 340])
        assert result.dual_values(lp.floor) == pytest.approx(coefficient - 0.43, abs=1e-6)
