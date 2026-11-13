from itertools import product

import pytest

from epsilon import max_epsilon


def order_kept(primary, secondary, eps) -> bool:
    """For every pair of plans with different main scores, the combined score agrees."""
    routes = list(primary)
    plans = list(product([0, 1], repeat=len(routes)))
    main = [sum(p * primary[r] for p, r in zip(plan, routes)) for plan in plans]
    full = [m + eps * sum(p * secondary[r] for p, r in zip(plan, routes)) for m, plan in zip(main, plans)]
    return all((full[i] > full[j]) == (main[i] > main[j])
               for i in range(len(plans)) for j in range(len(plans)) if main[i] != main[j])


def test_the_weight_never_reorders_plans_on_a_simple_case():
    primary, secondary = {"R1": 1, "R2": 2, "R3": 3}, {"R1": 0.5, "R2": 0.0, "R3": 0.0}
    eps = max_epsilon(primary, secondary)
    assert eps == pytest.approx(1 / 1.5)
    assert order_kept(primary, secondary, eps)


def test_the_smallest_gap_is_the_greatest_common_divisor():
    primary, secondary = {"R1": 6, "R2": 10, "R3": 15}, {"R1": 1.0, "R2": 0.0, "R3": 0.0}
    eps = max_epsilon(primary, secondary)
    assert eps == pytest.approx(1 / 2)
    assert order_kept(primary, secondary, eps)


def test_the_largest_bonus_is_the_sum_of_all_bonuses():
    primary, secondary = {"R1": 2, "R2": 2, "R3": 2, "R4": 2}, {"R1": 1.0, "R2": 1.0, "R3": 1.0, "R4": 1.0}
    eps = max_epsilon(primary, secondary)
    assert eps == pytest.approx(2 / 5)
    assert order_kept(primary, secondary, eps)
