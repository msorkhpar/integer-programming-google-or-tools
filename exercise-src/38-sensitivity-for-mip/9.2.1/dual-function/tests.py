from price_function import is_dual_feasible

HOURS, SILT = [2, 3], [3, 5]           # two job types


def value_function(D):
    z = [0] * (D + 1)
    for d in range(1, D + 1):
        z[d] = max([z[d - 1]] + [z[d - a] + c for a, c in zip(HOURS, SILT) if a <= d])
    return z


def test_the_value_function_passes_and_a_low_linear_price_fails():
    assert is_dual_feasible([2.0 * d for d in range(11)], HOURS, SILT) is True
    assert is_dual_feasible([1.5 * d for d in range(11)], HOURS, SILT) is False


def test_superadditivity_is_checked_for_unequal_pairs_too():
    F = value_function(8)
    F[5] = 7                            # the value function has 8 here; F(2) + F(3) = 3 + 5 > 7
    assert is_dual_feasible(value_function(8), HOURS, SILT) is True
    assert is_dual_feasible(F, HOURS, SILT) is False


def test_a_negative_value_for_one_unused_unit_is_refused():
    # One job type: 2 hours, 3 units. F is superadditive and covers the column, yet F(3) = 2 is
    # below a real schedule (one job and an unused hour: 3). Only F(1) >= 0 rules it out.
    F = [0, -1, 3, 2, 6, 5, 9]
    assert is_dual_feasible([0, 0, 3, 3, 6, 6, 9], [2], [3]) is True
    assert is_dual_feasible(F, [2], [3]) is False


def test_a_column_met_with_equality_is_allowed():
    assert is_dual_feasible([0, 0, 3, 5, 6, 8], HOURS, SILT) is True
