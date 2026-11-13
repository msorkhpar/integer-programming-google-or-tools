"""The module 04 examples: the program-split LP, its standard and equality forms, and three LP patterns."""

import math

import pytest
from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import activity, build, small

GLOP = mathopt.SolverType.GLOP


def solve(model):
    result = mathopt.solve(model, GLOP)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    return result


def test_the_first_lp_spends_less_than_the_budget_and_obeys_every_row():
    split = build(2027)
    result = solve(split.model)
    assert result.objective_value() == pytest.approx(4611.5, abs=0.05)
    for row in split.rows.values():
        a = activity(row, result)
        assert row.lower_bound - 1e-6 <= a <= row.upper_bound + 1e-6
    assert small.budget[2027] - activity(split.rows["budget"], result) == pytest.approx(230.3, abs=0.05)
    amounts = {k: result.variable_values(v) for k, v in split.s.items()}
    assert amounts["transmission"] == pytest.approx(amounts["distribution"] + amounts["vegetation"])


def test_dividing_by_an_expression_is_refused():
    model = mathopt.Model()
    a, b = model.add_variable(), model.add_variable()
    with pytest.raises(TypeError):
        model.add_linear_constraint(a / (a + b) <= 0.5)


def test_more_distribution_crews_make_the_budget_bind():
    import what_if
    crews = {k: small.crews[k, 2027] for k in PROGRAMS}
    split = build(2027, crews={**crews, "distribution": 12})
    result = solve(split.model)
    assert "budget" in what_if.full_rows(split, result)
    assert "crew_distribution" not in what_if.full_rows(split, result)
    assert result.objective_value() > solve(build(2027).model).objective_value()


def test_the_standard_form_has_the_same_optimum_and_negates_the_floor():
    import standard_form
    split = build(2027)
    c, A, b, labels, _ = standard_form.to_standard_form(split.model)
    assert standard_form.solve_matrix(c, A, b) == pytest.approx(solve(split.model).objective_value())
    floor = labels.index("floor_vegetation (x -1)")
    assert b[floor] == -300 and A[floor].min() == -1


def test_a_minimization_is_turned_into_a_maximization_of_the_negated_objective():
    import standard_form
    model = mathopt.Model()
    x = model.add_variable(lb=0)
    model.add_linear_constraint(x >= 2)
    model.minimize(3 * x)
    c, A, b, _, _ = standard_form.to_standard_form(model)
    assert list(c) == [-3] and standard_form.solve_matrix(c, A, b) == pytest.approx(-6)


def test_slack_and_surplus_variables_equal_each_rows_room():
    import slack_surplus
    model, extra = slack_surplus.equality_form()
    result = solve(model)
    split = build(2027)
    check = solve(split.model)
    assert result.objective_value() == pytest.approx(check.objective_value())
    for name, var in extra.items():
        row = split.rows[name]
        room = (row.upper_bound - activity(row, check)) if math.isfinite(row.upper_bound) \
            else activity(row, check) - row.lower_bound
        assert result.variable_values(var) == pytest.approx(room, abs=1e-6)


def test_loosening_a_row_with_room_changes_nothing_and_a_full_row_changes_the_answer():
    base = solve(build(2027).model).objective_value()
    assert solve(build(2027, budget=small.budget[2027] + 200).model).objective_value() == pytest.approx(base)
    assert solve(build(2027, floor={}).model).objective_value() == pytest.approx(base)
    crews = {k: small.crews[k, 2027] for k in PROGRAMS}
    assert solve(build(2027, crews={**crews, "vegetation": 3}).model).objective_value() > base + 1


def test_carry_over_never_loses_value_and_with_no_carry_it_is_the_yearly_model():
    import carry_over_lp
    plain, _, _ = carry_over_lp.build_years(carry=False)
    carry, _, r = carry_over_lp.build_years(carry=True)
    with_carry = solve(carry).objective_value()
    assert with_carry > solve(plain).objective_value()
    for var in r.values():
        var.upper_bound = 0
    assert solve(carry).objective_value() == pytest.approx(solve(plain).objective_value())


def test_the_blend_meets_the_average_and_a_per_contractor_rule_is_infeasible():
    import blend
    model, h = blend.buy(blend=True)
    result = solve(model)
    hours = {c: result.variable_values(v) for c, v in h.items()}
    assert sum(hours.values()) == pytest.approx(blend.HOURS)
    assert sum(blend.CONTRACTORS[c][1] * x for c, x in hours.items()) / blend.HOURS <= blend.TARGET + 1e-9
    strict, _ = blend.buy(blend=False, per_contractor=True)
    assert mathopt.solve(strict, GLOP).termination.reason == mathopt.TerminationReason.INFEASIBLE


def test_the_flow_meets_every_demand_and_its_flows_are_whole_numbers():
    import flow
    result = flow.result
    assert result.objective_value() == pytest.approx(299)
    values = {a: result.variable_values(v) for a, v in flow.f.items()}
    for n, amount in flow.DEMAND.items():
        got = sum(x for (i, j), x in values.items() if j == n) - sum(x for (i, j), x in values.items() if i == n)
        assert got == pytest.approx(amount)
    assert all(abs(x - round(x)) < 1e-6 for x in values.values())


def test_the_or_tools_sample_lp_is_decided_by_rows_c1_and_c3():
    from or_tools_lp import build as build_sample
    model, x, rows = build_sample()
    result = solve(model)
    assert result.objective_value() == pytest.approx(2200 / 3)
    assert [result.variable_values(v) for v in x] == [pytest.approx(100 / 3), pytest.approx(200 / 3), pytest.approx(0)]
    room = {row.name: row.upper_bound - activity(row, result) for row in rows}
    assert room == {"c1": pytest.approx(0, abs=1e-6), "c2": pytest.approx(100), "c3": pytest.approx(0, abs=1e-6)}


def test_the_stigler_diet_costs_39_66_a_year_with_five_foods_and_five_tight_nutrients():
    from stigler_diet import FOODS, NUTRIENTS, build as build_diet
    model, spend, rows = build_diet()
    result = solve(model)
    assert len(FOODS) == 77 and len(NUTRIENTS) == 9
    assert 365 * result.objective_value() == pytest.approx(39.66, abs=0.005)
    bought = [food for food, var in spend.items() if result.variable_values(var) > 1e-9]
    assert len(bought) == 5 and "Navy Beans, Dried" in bought
    tight = [n for n, row in rows.items() if activity(row, result) - row.lower_bound <= 1e-6]
    assert len(tight) == 5 and "Protein (g)" not in tight
