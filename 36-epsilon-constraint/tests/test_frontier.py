"""The module 36 examples: ε-constraint, AUGMECON, the exact frontier and the planner's reading of it."""

import itertools
from dataclasses import replace

import pytest
from ortools.math_opt.python import mathopt

from frontier import (Point, augmecon, dominated, dominates, epsilon_constraint, exact_frontier, grid,
                      payoff_table, supported)
from gridcap import generate
from objectives import build
from planner import best_reaching, knees, steps

# A tiny two-objective knapsack, solved both by the generator and by listing every subset.
ITEMS = [(4, 7, 5), (6, 3, 4), (5, 5, 5), (2, 8, 4), (7, 2, 6), (3, 6, 3)]   # (value a, value b, weight)
CAPACITY = 13


def knapsack():
    model = mathopt.Model()
    x = [model.add_binary_variable() for _ in ITEMS]
    model.add_linear_constraint(sum(w * v for (_, _, w), v in zip(ITEMS, x)) <= CAPACITY)
    a = mathopt.LinearExpression() + sum(i[0] * v for i, v in zip(ITEMS, x))
    b = mathopt.LinearExpression() + sum(i[1] * v for i, v in zip(ITEMS, x))
    return model, a, b


def brute_force_front():
    scores = set()
    for pick in itertools.product((0, 1), repeat=len(ITEMS)):
        if sum(w * p for (_, _, w), p in zip(ITEMS, pick)) <= CAPACITY:
            scores.add((sum(i[0] * p for i, p in zip(ITEMS, pick)), sum(i[1] * p for i, p in zip(ITEMS, pick))))
    pts = [Point(a, b) for a, b in scores]
    return {(p.first, p.second) for p in pts if not any(dominates(q, p) for q in pts)}


def test_the_exact_frontier_is_every_nondominated_point():
    model, a, b = knapsack()
    points, solves = exact_frontier(model, a, b, step=1)
    assert {(round(p.first), round(p.second)) for p in points} == brute_force_front()
    assert dominated(points) == []
    assert solves <= len(points) + 1


def test_augmecon_never_returns_a_dominated_plan_on_ties():
    model = mathopt.Model()
    x, z = model.add_binary_variable(), model.add_binary_variable()
    model.add_linear_constraint(x + z <= 2)
    first = mathopt.LinearExpression() + 5 * x               # z adds nothing to the first objective
    second = mathopt.LinearExpression() + 1 * x + 3 * z
    point, slack = augmecon(model, first, second, 0, span=4)
    assert (point.first, point.second) == pytest.approx((5, 4))
    assert slack == pytest.approx(4)


def test_grid_includes_both_ends():
    assert grid(10, 20, 3) == [10, 15, 20]


def test_knees_are_where_the_price_jumps():
    hull = [Point(0, 100), Point(10, 99), Point(20, 97), Point(30, 80)]
    assert [k[0] for k in knees(hull)] == [Point(10, 99), Point(20, 97)]
    assert [round(s.price, 2) for s in steps(hull)] == [0.1, 0.2, 1.7]
    assert best_reaching(hull, 15) == Point(20, 97)


@pytest.fixture(scope="module")
def two():
    return build(generate("small"))


def test_the_payoff_table_matches_lesson_734(two):
    npv_plan, risk_plan = payoff_table(two.model, two.npv, two.risk)
    assert (round(npv_plan.first), round(npv_plan.second)) == (24_260, 10_577)
    assert (round(risk_plan.first), round(risk_plan.second)) == (18_886, 16_086)


def test_one_floor_keeps_23815_of_npv(two):
    p = epsilon_constraint(two.model, two.npv, two.risk, 13_000)
    assert (round(p.first), round(p.second)) == (23_815, 13_221)
    assert epsilon_constraint(two.model, two.npv, two.risk, 16_200) is None


def test_plain_epsilon_returns_weak_plans_when_vegetation_has_no_npv():
    small = generate("small")
    variant = replace(small, projects=tuple(
        replace(p, npv={s: 0 for s in p.npv}) if p.program == "vegetation" else p for p in small.projects))
    t = build(variant)
    a, b = payoff_table(t.model, t.npv, t.risk)
    weak = 0
    for floor in grid(a.second, b.second, 11):
        plain = epsilon_constraint(t.model, t.npv, t.risk, floor)
        aug, _ = augmecon(t.model, t.npv, t.risk, floor, b.second - a.second)
        assert aug.first == pytest.approx(plain.first, abs=1e-4)
        assert not dominates(plain, aug)
        weak += dominates(aug, plain)
    assert weak == 6


def test_the_gridcap_frontier_has_65_nondominated_plans_and_three_knees(two):
    points, solves = exact_frontier(two.model, two.risk, two.npv)
    assert len(points) == solves == 65
    assert dominated(points) == []
    hull = supported(points)
    assert len(hull) == 8
    assert [round(p.first) for p, _, _ in knees(hull)] == [12_348, 14_466, 15_554]
