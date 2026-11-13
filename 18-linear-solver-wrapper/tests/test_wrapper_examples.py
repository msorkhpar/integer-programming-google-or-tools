"""The module 18 examples: the pywraplp script and its MathOpt port, the graph solvers, and the
special-purpose solvers, each checked against a MIP or an LP."""

import pytest
from ortools.algorithms.python import knapsack_solver
from ortools.graph.python import linear_sum_assignment, max_flow, min_cost_flow
from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt

from bin_packing import first_fit_decreasing, lower_bound, pack
from crews import CREWS, cost_table
from gridcap import generate
from legacy_selection import solve_legacy
from ported_selection import build, quiet_solve, solve_ported
from spares_network import ARCS, DEMAND, NAMES, NODE, SUPPLY


# ---- 4.7.1 and 4.7.2: the legacy script and its port agree


@pytest.mark.parametrize("size", ["tiny", "small", "medium"])
def test_the_port_reaches_the_legacy_value_and_plan_at_zero_gap(size):
    portfolio = generate(size)
    status, old_value, old_plan, _ = solve_legacy(portfolio, relative_gap=0.0)
    reason, new_value, new_plan, _ = solve_ported(portfolio, relative_gap=0.0)
    assert status == pywraplp.Solver.OPTIMAL
    assert reason == mathopt.TerminationReason.OPTIMAL
    assert new_value == pytest.approx(old_value, abs=1e-6)
    assert sorted(new_plan) == sorted(old_plan)


def test_the_port_has_the_same_rows_by_name():
    small = generate("small")
    _, _, _, solver = solve_legacy(small)
    model, _ = build(small)
    assert {c.name() for c in solver.constraints()} == {c.name for c in model.linear_constraints()}
    assert solver.NumVariables() == len(list(model.variables()))


def test_one_model_gives_one_value_on_three_solvers():
    model, _ = build(generate("small"))
    exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)
    values = {s: quiet_solve(model, s, exact).objective_value()
              for s in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT)}
    assert len(set(round(v, 6) for v in values.values())) == 1


def test_an_infeasible_pywraplp_solve_still_answers_value_queries_with_zero():
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = solver.IntVar(0, 3, "x")
    solver.Add(x >= 5)
    solver.Minimize(x)
    assert solver.Solve() == pywraplp.Solver.INFEASIBLE
    assert x.solution_value() == 0.0


# ---- 4.7.3: the flow solvers


def test_the_spares_min_cost_flow_matches_the_lp_of_lesson_2_1_3():
    smcf = min_cost_flow.SimpleMinCostFlow()
    for (i, j), (cost, cap) in ARCS.items():
        smcf.add_arc_with_capacity_and_unit_cost(NODE[i], NODE[j], cap, cost)
    for depot, shelf in SUPPLY.items():
        smcf.set_node_supply(NODE[depot], shelf)
    for region, need in DEMAND.items():
        smcf.set_node_supply(NODE[region], -need)
    assert smcf.solve() == smcf.UNBALANCED
    assert smcf.solve_max_flow_with_min_cost() == smcf.OPTIMAL
    assert smcf.maximum_flow() == sum(DEMAND.values())
    assert smcf.optimal_cost() == 299


def test_the_spares_max_flow_meets_every_demand_and_its_cut_is_tight():
    source, sink = len(NAMES), len(NAMES) + 1
    smf = max_flow.SimpleMaxFlow()
    for depot, shelf in SUPPLY.items():
        smf.add_arc_with_capacity(source, NODE[depot], shelf)
    for (i, j), (_, cap) in ARCS.items():
        smf.add_arc_with_capacity(NODE[i], NODE[j], cap)
    for region, need in DEMAND.items():
        smf.add_arc_with_capacity(NODE[region], sink, need)
    assert smf.solve(source, sink) == smf.OPTIMAL
    cut = set(smf.get_source_side_min_cut())
    across = sum(smf.capacity(a) for a in range(smf.num_arcs()) if smf.tail(a) in cut and smf.head(a) not in cut)
    assert smf.optimal_flow() == across == sum(DEMAND.values())


# ---- 4.7.4: assignment, knapsack, bin packing


def test_linear_sum_assignment_matches_the_mip_on_the_crews():
    tiny = generate("tiny")
    sites = [p.project_id for p in tiny.projects]
    cost = cost_table(tiny)
    lsa = linear_sum_assignment.SimpleLinearSumAssignment()
    for (c, s), k in cost.items():
        lsa.add_arc_with_cost(CREWS.index(c), sites.index(s), k)
    assert lsa.solve() == lsa.OPTIMAL
    assert all((CREWS[i], sites[lsa.right_mate(i)]) in cost for i in range(len(CREWS)))
    model = mathopt.Model()
    x = {pair: model.add_binary_variable() for pair in cost}
    for c in CREWS:
        model.add_linear_constraint(sum(v for (cc, _), v in x.items() if cc == c) == 1)
    for s in sites:
        model.add_linear_constraint(sum(v for (_, ss), v in x.items() if ss == s) == 1)
    model.minimize(sum(k * x[pair] for pair, k in cost.items()))
    assert mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value() == pytest.approx(lsa.optimal_cost())


def test_linear_sum_assignment_refuses_a_rectangular_table():
    a = linear_sum_assignment.SimpleLinearSumAssignment()
    for w in range(3):
        for t in range(2):
            a.add_arc_with_cost(w, t, w + t)
    assert a.solve() == a.INFEASIBLE


def test_knapsack_solver_matches_a_mip_on_the_season():
    small = generate("small")
    work = [p for p in small.projects if p.program in ("distribution", "vegetation")]
    solver = knapsack_solver.KnapsackSolver(knapsack_solver.SolverType.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "t")
    solver.init([p.value for p in work], [[p.crew_months for p in work]], [12])
    best = solver.solve()
    model = mathopt.Model()
    x = [model.add_binary_variable() for _ in work]
    model.add_linear_constraint(sum(p.crew_months * xi for p, xi in zip(work, x)) <= 12)
    model.maximize(sum(p.value * xi for p, xi in zip(work, x)))
    assert mathopt.solve(model, mathopt.SolverType.CP_SAT).objective_value() == pytest.approx(best)


@pytest.mark.parametrize("sizes, capacity, bins", [
    ([48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30], 100, 4),
    ([3, 3, 2, 2, 2, 2], 7, 2),
])
def test_bin_packing_places_every_item_within_capacity(sizes, capacity, bins):
    result, packing = pack(sizes, capacity, max_bins=len(sizes))
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert len(packing) == bins >= lower_bound(sizes, capacity)
    assert sorted(i for b in packing for i in b) == list(range(len(sizes)))
    assert all(sum(sizes[i] for i in b) <= capacity for b in packing)


def test_first_fit_decreasing_needs_a_third_bin_where_two_suffice():
    assert len(first_fit_decreasing([3, 3, 2, 2, 2, 2], 7)) == 3
