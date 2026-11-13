import itertools
import signal

import pytest
from ortools.math_opt.python import mathopt

from reel_pricing import best_reel


def brute(prices, pieces, reel):
    names = list(pieces)
    best = 0.0
    for counts in itertools.product(*[range(pieces[n][1] + 1) for n in names]):
        if sum(c * pieces[n][0] for n, c in zip(names, counts)) <= reel:
            best = max(best, sum(c * prices[n] for n, c in zip(names, counts)))
    return best


def check(prices, pieces, reel):
    value, pattern = best_reel(prices, pieces, reel)
    assert value == pytest.approx(brute(prices, pieces, reel))
    assert sum(pieces[n][0] * c for n, c in pattern.items()) <= reel
    assert all(0 < c <= pieces[n][1] for n, c in pattern.items())
    assert value == pytest.approx(sum(prices[n] * c for n, c in pattern.items()))
    return value, pattern


def test_the_most_valuable_cut_of_one_reel():
    pieces = {"feeder": (70, 5), "service": (50, 6), "lateral": (30, 6)}
    value, pattern = check({"feeder": 1.0, "service": 0.1, "lateral": 0.1}, pieces, 220)
    assert pattern == {"feeder": 3} and value == pytest.approx(3.0)


def test_a_reel_may_be_used_to_its_last_metre():
    pieces = {"feeder": (70, 5), "service": (50, 6), "lateral": (30, 6)}
    value, pattern = check({"feeder": 0.32, "service": 0.25, "lateral": 0.15}, pieces, 200)
    assert sum(pieces[n][0] * c for n, c in pattern.items()) == 200


def test_no_more_pieces_than_the_jobs_need():
    pieces = {"feeder": (70, 2), "service": (50, 6), "lateral": (30, 1)}
    value, pattern = check({"feeder": 1.0, "service": 0.3, "lateral": 0.25}, pieces, 300)
    assert pattern.get("feeder") == 2 and pattern.get("lateral", 0) <= 1


def knapsack(prices, pieces, reel):
    """The same pricing problem solved by HiGHS, to check a reel too long to try every pattern."""
    model = mathopt.Model()
    n = {k: model.add_integer_variable(lb=0, ub=d, name=k) for k, (_, d) in pieces.items()}
    model.add_linear_constraint(sum(length * n[k] for k, (length, _) in pieces.items()) <= reel)
    model.maximize(sum(prices[k] * n[k] for k in pieces))
    params = mathopt.SolveParameters(relative_gap_tolerance=0.0, absolute_gap_tolerance=0.0)
    return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params).objective_value()


def test_a_long_reel_is_priced_without_trying_every_pattern():
    pieces = {f"len{37 + 23 * i}": (37 + 23 * i, 30) for i in range(8)}
    prices = {k: float(length + 7 * (i % 3)) for i, (k, (length, _)) in enumerate(pieces.items())}

    def too_slow(*_):
        raise AssertionError("best_reel took over 10 s: 31**8 patterns are too many to try one by one")

    previous = signal.signal(signal.SIGALRM, too_slow)
    signal.alarm(10)
    try:
        value, pattern = best_reel(prices, pieces, 1000)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
    assert value == pytest.approx(knapsack(prices, pieces, 1000))
    assert sum(pieces[n][0] * c for n, c in pattern.items()) <= 1000
    assert all(0 < c <= pieces[n][1] for n, c in pattern.items())
    assert value == pytest.approx(sum(prices[n] * c for n, c in pattern.items()))
