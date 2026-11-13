"""The module 09 examples compute what their lessons say they print."""

import random

import pytest

from bnb import branch_and_bound, fractional
from gridcap import generate
from knapsack import Item, brute_force, by_ratio, dantzig_bound, gridcap_knapsack, solve
from selection import build, knapsack_model, solve_lp, solve_milp

TINY = generate("tiny")


def test_the_relaxation_bounds_the_tiny_optimum_from_above():
    lp = solve_lp(build(TINY), {})
    assert lp.value == pytest.approx(3770.1, abs=0.05)
    assert fractional(lp.x) == ["P003", "P004"]
    assert solve_milp(build(TINY, integer=True)).objective_value() == pytest.approx(3627)


def test_the_first_branch_splits_the_allowed_plans_22_and_10():
    import first_branch
    assert (len(first_branch.good), len(first_branch.down), len(first_branch.up)) == (32, 22, 10)
    sel = build(TINY)
    assert solve_lp(sel, {"P003": 0}).value == pytest.approx(3695.5, abs=0.05)
    assert solve_lp(sel, {"P003": 1}).value == pytest.approx(3054.7, abs=0.05)


def test_the_full_tree_has_29_nodes_and_finds_the_milp_optimum():
    search = branch_and_bound(build(TINY), prune=False)
    assert len(search.steps) == 29 and search.value == pytest.approx(3627)
    assert search.plan == ["P001", "P002", "P005", "P006"]


def test_pruning_cuts_the_tiny_tree_to_21_nodes_and_a_head_start_to_9():
    sel = build(TINY)
    assert len(branch_and_bound(sel).steps) == 21
    assert len(branch_and_bound(sel, start=(3504, ["P001", "P002", "P006"])).steps) == 9


def test_best_first_takes_7_nodes_and_solves_5_lps_on_tiny():
    search = branch_and_bound(build(TINY), node_rule="best")
    assert (len(search.steps), search.lps, search.value) == (7, 5, pytest.approx(3627))


def test_rounding_the_bound_saves_nodes_on_small():
    sel = build(generate("small"))
    plain, rounded = branch_and_bound(sel), branch_and_bound(sel, round_bound=True)
    assert (len(plain.steps), len(rounded.steps)) == (821, 803)
    assert plain.value == rounded.value == pytest.approx(25336)


def test_every_rule_reaches_the_highs_optimum_on_the_yearly_model():
    small = generate("small")
    best = solve_milp(build(small, integer=True, yearly=True)).objective_value()
    search = branch_and_bound(build(small, yearly=True), node_rule="best", var_rule="strong")
    assert search.value == pytest.approx(best) == pytest.approx(22532)
    assert (len(search.steps), search.lps) == (147, 375)


def test_dantzig_bound_equals_the_lp_relaxation():
    items, budget, _ = gridcap_knapsack(generate("small"))
    order, sel = by_ratio(items), knapsack_model(items, budget, integer=False)
    for fixed in ({}, {"P022": 0}, {"P022": 1}, {"P034": 0, "P031": 1}):
        assert dantzig_bound(order, budget, fixed).value == pytest.approx(solve_lp(sel, fixed).value)


@pytest.mark.parametrize("seed", range(20))
def test_the_knapsack_search_matches_brute_force(seed):
    rng = random.Random(seed)
    items = [Item(f"i{k}", rng.randint(1, 60), rng.randint(1, 40)) for k in range(12)]
    budget = sum(it.cost for it in items) // 2
    assert solve(items, budget).value == brute_force(items, budget)


def test_the_knapsack_search_matches_highs_on_the_gridcap_sizes():
    for size, value, nodes in (("tiny", 3021, 9), ("small", 23103, 735), ("medium", 203107, 743)):
        items, budget, _ = gridcap_knapsack(generate(size))
        result = solve(items, budget)
        assert (result.value, result.nodes) == (value, nodes)
        assert solve_milp(knapsack_model(items, budget)).objective_value() == pytest.approx(value)


def test_or_tools_knapsack_solver_agrees_with_our_search():
    from ortools_knapsack import CAPACITY, VALUES, WEIGHTS, ortools_solve
    value, packed = ortools_solve(VALUES, WEIGHTS, CAPACITY)
    assert value == 7534 and sum(WEIGHTS[i] for i in packed) == 850 and len(packed) == 32
    free = [i for i, w in enumerate(WEIGHTS) if w == 0]
    assert set(free) <= set(packed)
    ours = solve([Item(f"i{i}", v, w) for i, (v, w) in enumerate(zip(VALUES, WEIGHTS)) if w > 0], CAPACITY)
    assert ours.value + sum(VALUES[i] for i in free) == 7534
    items, budget, _ = gridcap_knapsack(generate("small"))
    assert ortools_solve([it.value for it in items], [it.cost for it in items], budget)[0] == 23103
