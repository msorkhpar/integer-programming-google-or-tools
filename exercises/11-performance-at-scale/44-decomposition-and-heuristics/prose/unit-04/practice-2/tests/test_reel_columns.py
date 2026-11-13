import math

import pytest
from ortools.math_opt.python import mathopt

from reel_columns import reel_columns

PIECES = {"feeder": (70, 9), "service": (50, 14), "lateral": (30, 11)}


def compact(pieces, reel, reels, integer):
    m = mathopt.Model()
    used = [m.add_variable(lb=0, ub=1, is_integer=integer) for _ in range(reels)]
    n = {(k, j): m.add_variable(lb=0, ub=d, is_integer=integer) for k, (_, d) in pieces.items() for j in range(reels)}
    for k, (_, d) in pieces.items():
        m.add_linear_constraint(sum(n[k, j] for j in range(reels)) >= d)
    for j in range(reels):
        m.add_linear_constraint(sum(length * n[k, j] for k, (length, _) in pieces.items()) <= reel * used[j])
    m.minimize(sum(used))
    return mathopt.solve(m, mathopt.SolverType.HIGHS).objective_value()


def test_one_piece_length_needs_no_new_pattern():
    lp, bounds, reels = reel_columns({"feeder": (70, 10)}, 220)
    assert lp == pytest.approx(10 / 3)
    assert reels == 4
    assert len(bounds) == 1


def test_patterns_are_added_until_none_has_a_negative_reduced_cost():
    lp, bounds, reels = reel_columns(PIECES, 220)
    assert len(bounds) > 1
    assert reels == round(compact(PIECES, 220, 16, True))
    assert lp >= compact(PIECES, 220, 16, False) - 1e-6
    assert reels >= math.ceil(lp - 1e-6)


def test_every_bound_sits_below_the_lp_optimum():
    lp, bounds, _ = reel_columns(PIECES, 220)
    assert len(bounds) > 1
    assert all(b <= lp + 1e-6 for b in bounds)
    assert bounds[-1] == pytest.approx(lp)
