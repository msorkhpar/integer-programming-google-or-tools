import pytest
from ortools.math_opt.python import mathopt

from street_trees import Street, build

# A city's streets, not the lesson's portfolio. Slopes: A 3, 1.4, 0.4; B 2, 1; C 4, 1.
A = Street("A", (0, 10, 25, 40), (0, 30, 51, 57))
B = Street("B", (0, 20, 50), (0, 40, 70))
C = Street("C", (0, 5, 15), (0, 20, 30))


def solve(streets, stock, fixed=None):
    model, trees = build(streets, stock)
    for name, value in (fixed or {}).items():
        trees[name].lower_bound = trees[name].upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return result.objective_value()


def test_the_best_planting_earns_the_most_benefit():
    # C's first 5 trees (4 each), A's first 10 (3), B's first 20 (2), then 5 more on A (1.4)
    assert solve([A, B, C], 40) == pytest.approx(97)


def test_a_street_earns_the_benefit_on_its_curve():
    assert solve([A], 100, {"A": 30}) == pytest.approx(53)       # 51 + 0.4 x 5
    assert solve([B], 100, {"B": 35}) == pytest.approx(55)       # 40 + 1 x 15


def test_no_street_takes_more_trees_than_its_curve_covers():
    assert solve([A], 100, {"A": 40}) == pytest.approx(57)
    assert solve([A], 100, {"A": 45}) is None
