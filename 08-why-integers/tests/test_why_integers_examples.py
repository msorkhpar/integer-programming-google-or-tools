"""The module 08 examples compute what their lessons say they print."""

import pytest

from gridcap import generate


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_the_relaxation_funds_part_of_p022_and_bounds_the_milp(small):
    from selection import best_plan, lp_values
    bound, values = lp_values(small)
    fractional = {pid: v for pid, v in values.items() if 1e-6 < v < 1 - 1e-6}
    assert list(fractional) == ["P022"] and fractional["P022"] == pytest.approx(0.522, abs=1e-3)
    optimum, plan = best_plan(small)
    assert bound == pytest.approx(25451.27, abs=0.01) and optimum == pytest.approx(25336)
    assert optimum <= bound


def test_rounding_up_breaks_the_budget_and_rounding_down_keeps_every_row(small):
    from rounding import fill, rounded
    from selection import best_plan, broken_rows, lp_values, value
    _, values = lp_values(small)
    assert broken_rows(small, rounded(values, "up")) == ["budget"]
    assert broken_rows(small, rounded(values, "nearest")) == ["budget"]
    down = rounded(values, "down")
    assert broken_rows(small, down) == [] and value(small, down) == 24671
    filled = fill(small, down)
    assert broken_rows(small, filled) == [] and value(small, filled) == 25290
    assert best_plan(small)[1] - down == {"P022", "P029"}


def test_broken_rows_names_each_rule():
    from selection import broken_rows
    tiny = generate("tiny")
    assert broken_rows(tiny, {"P001", "P002", "P005", "P006"}) == []
    assert broken_rows(tiny, {"P004", "P006", "P007"}) == ["must_P002", "parent_P004", "alt_G006"]


def test_the_hand_bound_matches_glop_on_the_budget_only_relaxation(small):
    from fractional_bound import budget_only_lp, greedy_bound
    from selection import lp_values
    bound, _ = greedy_bound(small)
    assert bound == pytest.approx(budget_only_lp(small))
    assert bound >= lp_values(small)[0] >= 25336


def test_the_loose_parent_row_raises_the_bound_and_keeps_the_optimum():
    from loose_parent import bound_and_optimum
    tiny = generate("tiny")
    tight, opt_tight, _ = bound_and_optimum(tiny, "tight")
    loose, opt_loose, _ = bound_and_optimum(tiny, "loose")
    assert loose > tight and opt_tight == pytest.approx(opt_loose) == pytest.approx(3627)


def test_the_gap_is_a_share_of_the_optimum():
    from gap_by_size import integrality_gap
    assert integrality_gap(101, 100) == pytest.approx(0.01)


def test_the_counting_table_agrees_with_listing_every_subset():
    from itertools import combinations
    from count_plans import count_within
    costs, budget = [20, 30, 40, 50, 70], 100
    listed = sum(sum(c) <= budget for k in range(len(costs) + 1) for c in combinations(costs, k))
    assert count_within(costs, budget) == listed


def test_the_bound_prunes_and_finds_the_same_best_plan():
    from tree_search import search
    items = [(30, 40), (20, 22), (50, 70), (40, 41), (10, 9), (60, 66)]
    best_plain, plain = search(items, 100, prune=False)
    best_pruned, pruned = search(items, 100, prune=True)
    assert best_plain == best_pruned and pruned < plain


def test_the_exact_split_puzzle_with_two_rows_has_no_solution():
    from ortools.math_opt.python import mathopt
    from selection import solve_highs
    from split_hardness import exact_split
    result = solve_highs(exact_split(2, 10, seed=1))
    assert result.termination.reason == mathopt.TerminationReason.INFEASIBLE


def test_the_or_tools_arrays_example_rounds_badly_and_its_optimum_is_260():
    import math
    from ortools.math_opt.python import mathopt
    from mip_arrays import OBJ, ROWS, RHS, broken, build
    model, x = build(integer=False)
    lp = mathopt.solve(model, mathopt.SolverType.GLOP)
    point = [lp.variable_values(v) for v in x]
    assert lp.objective_value() == pytest.approx(262.66, abs=0.01)
    assert sum(a * v for a, v in zip(ROWS[3], point)) == pytest.approx(RHS[3])       # c3 binds at the LP point
    assert broken([math.floor(v) for v in point]) == []
    assert broken([math.floor(v + 0.5) for v in point]) == ["c3"]
    assert broken([math.ceil(v) for v in point]) == ["c1", "c2", "c3"]
    for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP):
        model, x = build(integer=True)
        result = mathopt.solve(model, solver)
        assert result.objective_value() == pytest.approx(260) and result.solve_stats.node_count > 1
    assert sum(c * v for c, v in zip(OBJ, (10, 16, 4, 4, 3))) == 260 and broken([10, 16, 4, 4, 3]) == []


def test_the_seminar_assignment_has_a_whole_lp_answer_and_no_gap():
    from ortools.math_opt.python import mathopt
    from seminar import build, students
    ranked = students(num_classes=50, seed=1)
    for capacity, value in ((15, 24), (11, 50052)):
        lp = mathopt.solve(build(ranked, 50, capacity, integer=False), mathopt.SolverType.GLOP)
        assert lp.objective_value() == pytest.approx(value)
        assert all(min(v, 1 - v) < 1e-6 for v in lp.variable_values().values())
