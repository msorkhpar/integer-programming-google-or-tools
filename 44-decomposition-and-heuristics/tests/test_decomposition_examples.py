"""The module 44 examples: each decomposition checked against the model solved whole."""

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate

from capital import EXACT, build, schedule, solve_highs, value, violations

TOL = 1e-3


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def optimum(small):
    return solve_highs(build(small).model, EXACT).objective_value()


def test_every_nonnegative_price_bounds_the_optimum_and_matches_the_solver(small, optimum):
    from lagrange import lagrangian
    for price in (0.0, 0.2, 0.45, 0.8):
        lam = {y: price for y in small.years}
        bound, _ = lagrangian(small, lam)
        assert bound >= optimum - TOL
        cap = build(small, budget_rows=False)
        cap.model.maximize(cap.model.objective.as_linear_expression()
                           + sum(lam[y] * (small.budget[y] - cap.spend[y]) for y in small.years))
        assert solve_highs(cap.model, EXACT).objective_value() == pytest.approx(bound, abs=TOL)


def test_subgradient_brackets_the_optimum_and_stays_above_the_lp(small, optimum):
    from subgradient import subgradient
    best_bound, plan, history = subgradient(small, iterations=30)
    lp = solve_highs(build(small, integer=False).model).objective_value()
    assert violations(small, plan) == []
    assert value(small, plan) <= optimum + TOL <= best_bound + 2 * TOL
    assert best_bound >= lp - TOL


def test_benders_reaches_the_monolithic_optimum_and_plan(small):
    from benders import benders, monolithic, operating_cost
    best, plan, log = benders(small, verbose=False)
    cap, mono = monolithic(small)
    assert best == pytest.approx(mono.objective_value(), abs=TOL)
    assert plan == schedule(cap, mono)
    assert value(small, plan) - operating_cost(small, plan) == pytest.approx(best, abs=TOL)
    uppers = [upper for _, upper, _, _, _ in log]
    assert all(b <= a + TOL for a, b in zip(uppers, uppers[1:]))


def test_an_optimality_cut_is_exact_at_its_plan_and_below_the_cost_elsewhere(small):
    from benders import cut_expression
    from capital import crew_use
    from crew_costs import PROGRAMS, need_of, year_lp
    master = build(small)
    plan = schedule(master, solve_highs(master.model, EXACT))
    use = crew_use(small, master.x)
    y = 2029
    need = need_of(small, plan)
    m, rows = year_lp(small, y, {g: need[g, y] for g in PROGRAMS})
    sub = mathopt.solve(m, mathopt.SolverType.GLOP)
    cut = cut_expression(sub, rows, {g: use.get((g, y), mathopt.LinearExpression()) for g in PROGRAMS},
                         {g: small.crews[g, y] for g in PROGRAMS})
    point = {v: (1.0 if plan.get(pid) == t else 0.0) for (pid, t), v in master.x.items()}
    assert mathopt.evaluate_expression(cut, point) == pytest.approx(sub.objective_value(), abs=TOL)
    other = dict(plan)
    other.pop(next(pid for pid in plan if small.project(pid).program == "distribution"))
    other_need = need_of(small, other)
    m2, _ = year_lp(small, y, {g: other_need[g, y] for g in PROGRAMS})
    point2 = {v: (1.0 if other.get(pid) == t else 0.0) for (pid, t), v in master.x.items()}
    assert mathopt.evaluate_expression(cut, point2) <= mathopt.solve(m2, mathopt.SolverType.GLOP).objective_value() + TOL


def test_logic_based_benders_matches_the_one_cp_sat_model():
    import outage_check
    best, plan, iterations, cuts = outage_check.lbbd(outage_check.small, relaxation="year")
    assert best == pytest.approx(outage_check.solver.objective_value, abs=TOL)
    assert (iterations, cuts) == (11, 15)


def test_a_core_still_fails_and_drops_nothing_needed():
    from outages import jobs, schedulable, minimal_conflict
    outage = jobs(generate("small"))
    chosen = [outage[pid] for pid in ("P022", "P031", "P034")]
    core = minimal_conflict(chosen)
    assert not schedulable(core)
    assert all(schedulable([k for k in core if k is not j]) for j in core)


def test_column_generation_proves_its_integer_plan_optimal():
    import math
    from colgen import TASKS, column_generation
    lp, ip, used, history, columns = column_generation(verbose=False)
    assert lp == pytest.approx(33.1, abs=TOL) and ip == 34 == math.ceil(lp - 1e-6)
    for t, (_, need) in TASKS.items():
        assert sum(n * pattern.get(t, 0) for n, pattern in used) >= need
    assert all(sum(TASKS[t][0] * c for t, c in p.items()) <= 600 for _, p in used)
    bounds = [b for _, _, b, _, _ in history]
    assert all(b <= lp + TOL for b in bounds)


def test_rolling_horizon_and_lns_give_valid_plans_below_the_optimum(small):
    from lns import lns
    from rolling import rolling_horizon
    best = solve_highs(build(small, crews=True).model, EXACT).objective_value()
    plan, solves, _ = rolling_horizon(small, 2, 1)
    assert violations(small, plan, crews=True) == [] and value(small, plan) <= best + TOL
    better, _ = lns(small, plan, "years", 3, verbose=False)
    assert violations(small, better, crews=True) == []
    assert value(small, plan) <= value(small, better) <= best + TOL
