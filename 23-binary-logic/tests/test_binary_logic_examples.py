"""The module 23 examples: counting rows, logic rows, cardinality rules and product linearizations."""

import itertools

import pytest
from ortools.math_opt.python import mathopt

from clearance_width import width_model
from gridcap import REGIONS, generate
from selection_model import EXACT, allowed_values, build, funded, ids, solve_highs


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(sel):
    result = solve_highs(sel.model, EXACT)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    return result


def test_the_base_plan_and_its_counts(small):
    sel = build(small)
    result = solve(sel)
    plan = funded(sel, result)
    assert result.objective_value() == pytest.approx(25_336)
    assert len(plan) == 20
    assert sum(small.project(i).program == "transmission" for i in plan) == 8
    assert sum(small.project(i).capex for i in plan) <= small.capital_budget


@pytest.mark.parametrize("cap, npv", [(6, 25_159), (5, 24_845), (4, 23_927), (3, 21_932)])
def test_the_transmission_cap_keeps_the_count_and_costs_what_the_lesson_says(small, cap, npv):
    sel = build(small)
    transmission = ids(small, program="transmission")
    sel.model.add_linear_constraint(sum(sel.x[i] for i in transmission) <= cap)
    result = solve(sel)
    assert result.objective_value() == pytest.approx(npv)
    assert sum(i in transmission for i in funded(sel, result)) <= cap


def test_whole_mobilizations_cover_the_vegetation_projects(small):
    sel = build(small)
    vegetation = ids(small, program="vegetation")
    m = sel.model.add_variable(lb=0, is_integer=True)
    sel.model.add_linear_constraint(3 * m >= sum(sel.x[i] for i in vegetation))
    sel.budget.set_coefficient(m, 90)
    result = solve(sel)
    chosen = [i for i in funded(sel, result) if i in vegetation]
    assert result.variable_values(m) == pytest.approx(-(-len(chosen) // 3))
    assert result.objective_value() == pytest.approx(25_228)


@pytest.mark.parametrize("rows, logic, names", [
    (lambda m, v: m.add_linear_constraint(v["a"] <= v["b"]), lambda a, b: (not a) or b, "ab"),
    (lambda m, v: m.add_linear_constraint(v["a"] + v["b"] - 1 <= v["c"]), lambda a, b, c: not (a and b) or c, "abc"),
    (lambda m, v: m.add_linear_constraint(v["a"] <= v["b"] + v["c"]), lambda a, b, c: (not a) or b or c, "abc"),
])
def test_each_implication_row_allows_exactly_its_truth_table(rows, logic, names):
    want = [vals for vals in itertools.product((0, 1), repeat=len(names)) if logic(*vals)]
    assert allowed_values(rows, tuple(names)) == want


def test_the_and_rows_pin_z_to_the_product():
    def rows(m, v):
        m.add_linear_constraint(v["z"] <= v["a"])
        m.add_linear_constraint(v["z"] <= v["b"])
        m.add_linear_constraint(v["z"] >= v["a"] + v["b"] - 1)
    assert allowed_values(rows, ("a", "b", "z")) == [(a, b, a * b) for a in (0, 1) for b in (0, 1)]


def test_one_row_and_pair_rows_give_the_same_milp_and_the_one_row_lp_is_tighter(small):
    valley = ids(small, program="transmission", region="Valley")
    values = {}
    for form in ("one", "pairs"):
        for integer in (True, False):
            sel = build(small, integer=integer)
            if form == "one":
                sel.model.add_linear_constraint(sum(sel.x[i] for i in valley) <= 1)
            else:
                for a, b in itertools.combinations(valley, 2):
                    sel.model.add_linear_constraint(sel.x[a] + sel.x[b] <= 1)
            result = solve(sel) if integer else mathopt.solve(sel.model, mathopt.SolverType.GLOP)
            values[form, integer] = result.objective_value()
    assert values["one", True] == pytest.approx(values["pairs", True])
    assert values["one", False] < values["pairs", False]


def test_the_switch_gives_each_region_none_or_at_least_two_vegetation_jobs(small):
    sel = build(small)
    for r in REGIONS:
        members = ids(small, program="vegetation", region=r)
        g = sel.model.add_binary_variable()
        jobs = sum(sel.x[i] for i in members)
        sel.model.add_linear_constraint(jobs >= 2 * g)
        sel.model.add_linear_constraint(jobs <= len(members) * g)
    plan = funded(sel, solve(sel))
    for r in REGIONS:
        assert sum(i in plan for i in ids(small, program="vegetation", region=r)) in {0, 2, 3, 4}


def test_the_linearized_pair_bonus_matches_the_product_on_its_plan(small):
    pairs = [p for r in REGIONS for p in itertools.combinations(ids(small, program="distribution", region=r), 2)]
    sel = build(small)
    z = {}
    for a, b in pairs:
        z[a, b] = sel.model.add_binary_variable()
        sel.model.add_linear_constraint(z[a, b] <= sel.x[a])
        sel.model.add_linear_constraint(z[a, b] <= sel.x[b])
        sel.model.add_linear_constraint(z[a, b] >= sel.x[a] + sel.x[b] - 1)
    sel.model.maximize(sel.model.objective.as_linear_expression() + sum(150 * v for v in z.values()))
    result = solve(sel)
    plan = set(funded(sel, result))
    true_value = sum(small.project(i).value for i in plan) + 150 * sum(a in plan and b in plan for a, b in pairs)
    assert result.objective_value() == pytest.approx(true_value)
    assert result.objective_value() == pytest.approx(26_064)


def test_the_width_model_reproduces_the_standard_plan_and_w_equals_x_times_q(small):
    sel, q, w = width_model(small, fixed=4.0)
    assert solve(sel).objective_value() == pytest.approx(25_336)
    sel, q, w = width_model(small)
    result = solve(sel)
    for i, var in w.items():
        assert result.variable_values(var) == pytest.approx(
            round(result.variable_values(sel.x[i])) * result.variable_values(q), abs=1e-6)


def test_a_looser_bound_in_the_rows_weakens_the_lp_and_a_smaller_one_cuts_the_milp(small):
    lp = {}
    for high in (6.0, 60.0):
        sel, q, w = width_model(small, integer=False, high_in_rows=high)
        lp[high] = mathopt.solve(sel.model, mathopt.SolverType.GLOP).objective_value()
    assert lp[6.0] < lp[60.0]
    true_best = solve(width_model(small)[0]).objective_value()
    assert solve(width_model(small, high_in_rows=5.0)[0]).objective_value() < true_best - 1


def test_the_team_rule_is_a_count_and_raises_the_cost_to_the_guides_250():
    from teams import solve as solve_teams
    status, cost, counts, _ = solve_teams(None)
    assert (status, cost, max(counts.values())) == ("OPTIMAL", pytest.approx(235), 3)
    status, cost, counts, pairs = solve_teams(2)
    assert (status, cost) == ("OPTIMAL", pytest.approx(250))
    assert all(n <= 2 for n in counts.values()) and len(pairs) == 4
    assert solve_teams(1)[0] == "INFEASIBLE"


def test_cpsat_logic_allows_exactly_what_the_linear_rows_allow():
    from cpsat_logic import all_solutions, linear_rows
    by_rows = allowed_values(linear_rows, ("b", "x", "y"))
    for version in ("bool_and", "implication", "bool_or"):
        assert all_solutions(version) == by_rows
    assert by_rows == [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 1, 0)]


def test_nurse_schedules_count_and_the_minimum_that_leaves_none():
    from nurses import schedules
    assert schedules(2, 3) == ("OPTIMAL", 5184)
    assert schedules(2, None) == ("OPTIMAL", 5184)
    assert schedules(3, None) == ("INFEASIBLE", 0)


def test_cpsat_products_list_the_and_table_and_b_times_x():
    from cpsat_products import bool_times_int, boolean_product
    assert boolean_product() == [(x, y, x * y) for x in (0, 1) for y in (0, 1)]
    assert bool_times_int(1, 4) == sorted((b, x, b * x) for b in (0, 1) for x in range(1, 5))
