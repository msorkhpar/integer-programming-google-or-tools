"""The module 25 examples: knapsacks, multiple knapsacks, crew assignment and cover cuts."""

import itertools

import pytest
from ortools.math_opt.python import mathopt

from best_by_table import best_plan
from covers import extension, is_cover, minimal, separate
from gridcap import generate
from knapsack_models import (CAPACITY, CONTRACTOR, CREWS, EXACT, assignment_model, base_plan, capital_row, chosen,
                             discretionary, eligible, knapsack_model, size, solve_highs, year_rows)


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(model, params=EXACT):
    result = solve_highs(model, params)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    return result


def values_of(portfolio):
    return {p.project_id: p.value for p in discretionary(portfolio)}


def test_one_row_and_six_rows_give_the_lesson_values(small):
    rows = [capital_row(small)] + year_rows(small)
    assert solve(knapsack_model(values_of(small), rows[:1])[0]).objective_value() == pytest.approx(23_103)
    assert solve(knapsack_model(values_of(small), rows)[0]).objective_value() == pytest.approx(20_183)


def test_the_table_matches_brute_force_on_random_knapsacks():
    import random
    rng = random.Random(25)
    for _ in range(20):
        items = [(f"i{k}", rng.randint(1, 30), rng.randint(1, 15)) for k in range(10)]
        budget = rng.randint(10, 60)
        best, plan = best_plan(items, budget)
        brute = max(sum(v for _, v, _ in chosen_items)
                    for r in range(len(items) + 1) for chosen_items in itertools.combinations(items, r)
                    if sum(c for _, _, c in chosen_items) <= budget)
        assert best[-1] == brute
        assert sum(c for n, _, c in items if n in plan) <= budget
        assert sum(v for n, v, _ in items if n in plan) == brute


def test_the_lp_has_at_most_one_fraction_per_row(small):
    rows = [capital_row(small)] + year_rows(small)
    for use in (rows[:1], rows):
        model, x = knapsack_model(values_of(small), use, integer=False)
        result = solve(model, None)
        fractional = [i for i, v in x.items() if 1e-6 < result.variable_values(v) < 1 - 1e-6]
        assert len(fractional) <= len(use)


def test_the_crew_assignment_costs_and_capacities(small):
    plan = base_plan(small)
    assert len(plan) == 20
    for only, cost in ((False, 2_135), (True, 2_290)):
        model, x = assignment_model(plan, only_eligible=only)
        result = solve(model)
        assert result.objective_value() == pytest.approx(cost)
        crew_of = dict(chosen(x, result))
        assert set(crew_of) == {p.project_id for p in plan}
        for k in CREWS + (CONTRACTOR,):
            assert sum(size(p, k) for p in plan if crew_of[p.project_id] == k) <= CAPACITY[k]
        if only:
            assert all(eligible(p, crew_of[p.project_id]) for p in plan)


def test_the_relaxed_assignment_splits_at_most_one_project_per_crew(small):
    plan = base_plan(small)
    model, x = assignment_model(plan, only_eligible=True, integer=False)
    result = solve(model, None)
    assert result.objective_value() == pytest.approx(2_258.75)
    split = {i for (i, k), v in x.items() if 1e-6 < result.variable_values(v) < 1 - 1e-6}
    assert len(split) <= len(CREWS) + 1


def test_every_cover_row_on_tiny_keeps_every_whole_plan():
    tiny = generate("tiny")
    row = capital_row(tiny)
    names = list(row.weight)
    plans = [set(c) for r in range(len(names) + 1) for c in itertools.combinations(names, r)
             if not is_cover(row, list(c))]
    xstar = {i: 0.5 for i in names}
    for r in range(1, len(names) + 1):
        for c in itertools.combinations(names, r):
            if not is_cover(row, list(c)):
                continue
            small_cover = minimal(row, list(c), xstar)
            assert is_cover(row, small_cover)
            left = small_cover + extension(row, small_cover)
            assert all(len(plan & set(left)) <= len(small_cover) - 1 for plan in plans)


def test_separation_finds_a_broken_cover_on_the_six_row_lp(small):
    rows = [capital_row(small)] + year_rows(small)
    model, x = knapsack_model(values_of(small), rows, integer=False)
    result = solve(model, None)
    xstar = {i: result.variable_values(v) for i, v in x.items()}
    broken = 0
    for row in rows:
        cover, slack = separate(row, xstar)
        if cover and slack < 1 - 1e-9:
            assert is_cover(row, cover)
            assert sum(xstar[i] for i in cover) > len(cover) - 1
            broken += 1
    assert broken == 5


def test_task_sizes_minimum_is_the_guides_326_and_the_lp_splits_few_tasks():
    from task_sizes import COSTS, gap
    model, x = gap()
    result = solve_highs(model, EXACT)
    assert result.objective_value() == pytest.approx(326)
    model, x = gap(integer=False)
    lp = mathopt.solve(model, mathopt.SolverType.GLOP)
    assert lp.objective_value() == pytest.approx(310.8)
    split = {t for (w, t), v in x.items() if 1e-6 < lp.variable_values(v) < 1 - 1e-6}
    assert len(split) <= len(COSTS)
