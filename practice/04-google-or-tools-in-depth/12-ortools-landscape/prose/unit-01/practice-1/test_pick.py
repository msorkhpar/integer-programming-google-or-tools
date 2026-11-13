import itertools
from fractions import Fraction

from pick import pick


def best_value(values, costs, budget):
    """The most value any affordable set has, by trying every set, in exact arithmetic."""
    best = 0
    for size in range(len(values) + 1):
        for chosen in itertools.combinations(range(len(values)), size):
            if sum(Fraction(str(costs[i])) for i in chosen) <= Fraction(str(budget)):
                best = max(best, sum(Fraction(str(values[i])) for i in chosen))
    return best


def check(values, costs, budget):
    chosen = pick(values, costs, budget)
    assert chosen == sorted(set(chosen)), "indices must be distinct and in increasing order"
    assert sum(Fraction(str(costs[i])) for i in chosen) <= Fraction(str(budget)), "over budget"
    assert sum(Fraction(str(values[i])) for i in chosen) == best_value(values, costs, budget)
    return chosen


def test_whole_number_data_gives_the_best_pick():
    check([12, 7, 9, 4, 6], [5, 3, 4, 2, 3], 9)
    check([20, 3, 3, 3, 3], [8, 2, 2, 2, 2], 8)


def test_the_pick_is_affordable_and_in_order():
    chosen = check([5, 8, 2, 6, 7, 3], [4, 6, 1, 3, 5, 2], 10)
    assert len(chosen) >= 2


def test_costs_with_cents_are_not_rounded_to_millions():
    assert check([5, 6, 7], [1.4, 1.4, 1.4], 4.0) == [1, 2]


def test_an_exact_fit_survives_floating_point():
    assert check([3, 4], [0.5, 0.65], 1.15) == [0, 1]
