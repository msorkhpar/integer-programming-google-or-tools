"""The module 11 examples compute what their lessons say they print."""

import math

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, mask_time, plan, solve_highs


@pytest.fixture(scope="module")
def medium():
    return generate("medium")


def test_the_selection_model_has_one_row_per_rule(medium):
    sel = build(medium)
    must = sum(p.must_do for p in medium.projects)
    alts = len({p.alt_group for p in medium.projects if p.alt_group})
    children = sum(1 for p in medium.projects if p.parent)
    rows = len(list(sel.model.linear_constraints()))
    assert (must, alts, children, len(sel.budget)) == (39, 18, 18, 10)
    assert rows == must + alts + children + len(medium.years) == 85
    assert len(sel.x) == 400


def test_the_bounds_bracket_the_optimum_and_the_lp_bounds_them_all(medium):
    sel = build(medium)
    lp = solve_highs(build(medium, integer=False).model).objective_value()
    r = solve_highs(sel.model, mathopt.SolveParameters(node_limit=100, relative_gap_tolerance=0.0))
    b = r.termination.objective_bounds
    assert r.termination.reason == mathopt.TerminationReason.FEASIBLE
    assert r.termination.limit == mathopt.Limit.NODE
    assert b.primal_bound == pytest.approx(224_315) and b.dual_bound == pytest.approx(224_552)
    assert b.primal_bound <= 224_384 <= b.dual_bound <= lp == pytest.approx(224_870.85, abs=0.01)


def test_a_gap_tolerance_ends_optimal_with_a_gap_above_zero(medium):
    sel = build(medium)
    r = solve_highs(sel.model, mathopt.SolveParameters(relative_gap_tolerance=0.01))
    b = r.termination.objective_bounds
    assert r.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert 0 < (b.dual_bound - b.primal_bound) / b.primal_bound <= 0.01


def test_a_node_limited_run_repeats_exactly(medium):
    sel = build(medium)
    params = mathopt.SolveParameters(node_limit=50, relative_gap_tolerance=0.0)
    first, second = solve_highs(sel.model, params), solve_highs(sel.model, params)
    assert first.termination.objective_bounds == second.termination.objective_bounds
    assert plan(sel, first) == plan(sel, second)


def test_highs_divides_its_gap_by_the_incumbent(medium):
    sel = build(medium)
    log: list[str] = []
    r = solve_highs(sel.model, mathopt.SolveParameters(solution_limit=1, enable_output=True), log=log)
    p, d = r.termination.objective_bounds.primal_bound, r.termination.objective_bounds.dual_bound
    gap_line = [line for line in log if line.strip().startswith("Gap")][-1]
    printed = float(gap_line.split()[1].rstrip("%"))
    assert printed == pytest.approx(100 * (d - p) / p, abs=0.05)
    assert printed != pytest.approx(100 * (d - p) / d, abs=0.05)


def test_an_infeasible_maximization_has_infinite_bounds_and_no_value(medium):
    import dataclasses
    short = dataclasses.replace(medium, budget={**medium.budget, 2027: 1_000})
    r = solve_highs(build(short).model)
    assert r.termination.reason == mathopt.TerminationReason.INFEASIBLE
    assert math.isinf(r.termination.objective_bounds.primal_bound)
    with pytest.raises(ValueError):
        r.objective_value()


def test_a_constant_in_the_objective_stops_the_same_tolerance_earlier(medium):
    sel = build(medium)
    npv = sum(p.value * sel.x[p.project_id] for p in medium.projects)
    params = mathopt.SolveParameters(relative_gap_tolerance=1e-4)
    sel.model.maximize(npv + 20_000_000)
    r = solve_highs(sel.model, params)
    b = r.termination.objective_bounds
    assert r.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert (b.dual_bound - b.primal_bound) / b.primal_bound <= 1e-4
    assert (b.dual_bound - b.primal_bound) / (b.primal_bound - 20_000_000) > 1e-3


def test_cp_sat_refuses_a_node_limit():
    sel = build(generate("small"))
    with pytest.raises(Exception):
        mathopt.solve(sel.model, mathopt.SolverType.CP_SAT, params=mathopt.SolveParameters(node_limit=10))


def test_masking_replaces_only_the_time_at_the_end():
    row = " R       0       0         0   0.00%   224870.849213   219607             2.40%        0      0      0        17     0.1s"
    assert mask_time(row).endswith("17     <t>s")
    assert mask_time("Gap               0.106%") == "Gap               0.106%"


def test_the_or_tools_scheduling_example_first_plan_is_far_from_the_optimum():
    from ortools.math_opt.python import mathopt
    from scheduling import build, random_jobs
    from selection import solve_highs
    assert solve_highs(build([10, 1, 5], [0, 1, 0])).objective_value() == pytest.approx(26)
    model = build(*random_jobs(15, seed=1))
    best = solve_highs(model)
    assert best.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert best.objective_value() == pytest.approx(1117)
    first = solve_highs(model, mathopt.SolveParameters(solution_limit=1, relative_gap_tolerance=0.0))
    assert first.termination.reason == mathopt.TerminationReason.FEASIBLE
    assert first.termination.limit == mathopt.Limit.SOLUTION
    assert first.objective_value() == pytest.approx(2273)
    assert first.termination.objective_bounds.dual_bound <= 1117 + 1e-6
