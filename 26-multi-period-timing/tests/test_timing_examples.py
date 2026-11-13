"""The module 26 examples: the timing model, cash-flow spreading, precedence forms, carry-over and budget pots."""

from dataclasses import replace

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build, schedule

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(tm):
    return mathopt.solve(tm.model, mathopt.SolverType.HIGHS, params=EXACT)


def test_the_schedule_respects_windows_must_dos_and_budgets(small):
    tm = build(small)
    plan = schedule(tm, solve(tm))
    for pid, t in plan.items():
        assert t in small.project(pid).starts()
    assert all(p.project_id in plan for p in small.projects if p.must_do)
    spend = {y: 0 for y in small.years}
    for pid, t in plan.items():
        for y, amount in small.project(pid).spend(t).items():
            spend[y] += amount
    assert all(spend[y] <= small.budget[y] for y in small.years)


def test_children_start_at_least_their_lag_after_their_parents(small):
    tm = build(small)
    plan = schedule(tm, solve(tm))
    for p in small.projects:
        if p.parent and p.project_id in plan:
            assert plan[p.project_id] >= plan[p.parent] + p.parent_lag


def test_spend_expressions_equal_the_calendar_spend_of_a_fixed_plan(small):
    tm = build(small)
    plan = schedule(tm, solve(tm))
    values = {v: 1.0 if (pid, t) in plan.items() else 0.0 for (pid, t), v in tm.x.items()}
    for y in small.years:
        want = sum(small.project(pid).spend(t).get(y, 0) for pid, t in plan.items())
        assert mathopt.evaluate_expression(tm.spend[y], values) == pytest.approx(want)


def test_the_lump_model_claims_more_than_the_spread_model(small):
    assert solve(build(small, cash_flow="lump")).objective_value() > solve(build(small)).objective_value()


def test_both_precedence_forms_give_the_same_milp_and_the_cumulative_lp_is_tighter(small):
    frozen = replace(small, budget={y: (0 if y in small.years[:2] else v) for y, v in small.budget.items()})
    milp = {f: solve(build(frozen, precedence=f)).objective_value() for f in ("aggregated", "cumulative")}
    assert milp["aggregated"] == pytest.approx(milp["cumulative"])
    lp = {f: mathopt.solve(build(frozen, integer=False, precedence=f).model, mathopt.SolverType.GLOP).objective_value()
          for f in ("aggregated", "cumulative")}
    assert lp["cumulative"] < lp["aggregated"]


def test_carry_over_adds_value_and_an_equality_cash_row_turns_infeasible():
    import carry_over
    base = solve(build(carry_over.small)).objective_value()
    unlimited, _ = carry_over.with_carry_over()
    assert unlimited.objective_value() > base
    cap = 10 * (9 * (carry_over.small.budget[2030] + carry_over.small.budget[2031]) // 100)
    strict, _ = carry_over.with_carry_over(max_share=0.1, window_cap=((2030, 2031), cap), lapse=False)
    assert strict.termination.reason == mathopt.TerminationReason.INFEASIBLE


def test_unlimited_carry_over_equals_a_cumulative_budget():
    import carry_over
    small = carry_over.small
    tm = build(small)
    for y in small.years:
        tm.model.delete_linear_constraint(tm.budget[y])
    for i, y in enumerate(small.years):
        tm.model.add_linear_constraint(sum(tm.spend[u] for u in small.years[: i + 1])
                                       <= sum(small.budget[u] for u in small.years[: i + 1]))
    unlimited, _ = carry_over.with_carry_over()
    assert solve(tm).objective_value() == pytest.approx(unlimited.objective_value())


def test_pot_rows_refuse_the_pooled_optimum_and_the_fund_2027_row_keeps_p034_out():
    import categories
    small = categories.small
    pooled = build(small)
    pooled_result = solve(pooled)
    spend = categories.pot_spend(schedule(pooled, pooled_result))
    assert all(sum(categories.B[k, y] for k in categories.POTS) == small.budget[y] for y in small.years)
    assert spend["fund", 2027] > categories.B["fund", 2027]          # the pooled plan breaks a pot row
    tm, result = categories.with_categories()
    assert result.objective_value() < pooled_result.objective_value()
    assert "P034" not in schedule(tm, result)
    gain = {f"{k}_{y}": categories.with_categories(drop=f"{k}_{y}")[1].objective_value() - result.objective_value()
            for k in categories.POTS for y in small.years}
    assert max(gain, key=gain.get) == "fund_2027"
    assert categories.B["fund", 2027] - categories.pot_spend(schedule(tm, result))["fund", 2027] > 0


def test_time_indexed_windows_as_bounds_or_never_created_give_the_same_schedule():
    from time_indexed import EXACT as EXACT_TI, random_jobs, time_indexed
    from timing_model import solve_highs as solve_ti
    for p, r in (([10, 1, 5], [0, 1, 0]), random_jobs(8, 3)):
        bounded, _ = time_indexed(p, r, "bounds")
        created, _ = time_indexed(p, r, "create")
        assert created.get_num_variables() < bounded.get_num_variables()
        assert solve_ti(created, EXACT_TI).objective_value() == pytest.approx(solve_ti(bounded, EXACT_TI).objective_value())


def test_time_indexed_lp_bound_beats_the_start_time_big_m_bound():
    from ortools.math_opt.python import mathopt as mo
    from time_indexed import random_jobs, start_time, time_indexed
    for p, r in (([10, 1, 5], [0, 1, 0]), random_jobs(8, 3)):
        ti, _ = time_indexed(p, r, "create", integer=False)
        assert mo.solve(ti, mo.SolverType.GLOP).objective_value() > \
            mo.solve(start_time(p, r, integer=False), mo.SolverType.GLOP).objective_value()


def test_plus_equals_on_an_expression_rebinds_and_leaves_the_old_object():
    from ortools.math_opt.python import mathopt as mo
    model = mo.Model()
    x = model.add_binary_variable(name="x")
    total = mo.LinearExpression()
    alias = total
    total += 360 * x
    assert total is not alias and len(alias.terms) == 0


def test_an_empty_sum_is_refused_as_a_row_and_accepted_from_a_linear_expression():
    tiny = generate("tiny")
    model = mathopt.Model()
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=True)
         for p in tiny.projects for t in p.starts()}
    regions = {p.region for p in tiny.projects}
    empty = [(g, y) for g in regions for y in tiny.years
             if not any(p.region == g and y in p.starts() for p in tiny.projects)]
    assert sorted(empty) == [("Coast", 2028), ("Coast", 2029)]
    with pytest.raises(TypeError):
        model.add_linear_constraint(sum(x[k] for k in []) <= 1)
    for g in regions:
        for y in tiny.years:
            starts = sum((x[p.project_id, t] for p in tiny.projects for t in p.starts()
                          if p.region == g and t == y), start=mathopt.LinearExpression())
            model.add_linear_constraint(starts <= 1)
    assert mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL
    floor = mathopt.Model()
    floor.add_linear_constraint(mathopt.LinearExpression() >= 1)
    assert mathopt.solve(floor, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.INFEASIBLE
