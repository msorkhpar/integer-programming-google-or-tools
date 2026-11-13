from itertools import product

from sweep import sweep


def by_hand(costs, values, must, budget):
    best = None
    for pick in product((0, 1), repeat=len(costs)):
        if any(pick[i] == 0 for i in must):
            continue
        if sum(c * p for c, p in zip(costs, pick)) <= budget:
            value = sum(v * p for v, p in zip(values, pick))
            best = value if best is None else max(best, value)
    return best


def test_each_budget_gets_the_best_value_of_any_plan():
    costs, values, budgets = [2, 3, 4], [6, 6, 4], [0, 2, 5, 9]
    assert sweep(costs, values, [], budgets) == [(b, by_hand(costs, values, [], b)) for b in budgets]


def test_a_required_upgrade_is_always_in():
    costs, values, must = [5, 4, 4], [2, 9, 9], [0]
    budgets = [9, 13]
    assert sweep(costs, values, must, budgets) == [(9, 11), (13, 20)]


def test_a_budget_below_the_required_upgrades_has_no_plan():
    costs, values, must = [5, 4, 4], [2, 9, 9], [0]
    assert sweep(costs, values, must, [4, 5]) == [(4, None), (5, 2)]


def test_an_upgrade_is_bought_whole_or_not_at_all():
    costs, values = [3, 3, 5], [4, 4, 5]
    budgets = [4, 7, 10]
    assert sweep(costs, values, [], budgets) == [(b, by_hand(costs, values, [], b)) for b in budgets]
