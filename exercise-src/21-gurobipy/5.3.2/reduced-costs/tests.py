import pytest

from pricing import reduced_costs, wrong_signs

# A workshop: chairs a, tables b, benches c; rows: saw hours, glue hours, finishing hours.
C = [3.0, 5.0, 4.0]
A = [[1.0, 0.0, 0.0],
     [0.0, 2.0, 1.0],
     [3.0, 2.0, 2.0]]
PI = [0.0, 1.5, 1.0]


def test_reduced_costs_charge_every_row_at_its_price():
    assert reduced_costs(C, A, PI) == pytest.approx([0.0, 0.0, 0.5])
    assert reduced_costs([2.0], [[4.0], [1.0]], [0.25, 0.5]) == pytest.approx([0.5])


def test_an_optimal_maximization_has_no_wrong_signs():
    rc = reduced_costs(C[:2], [row[:2] for row in A], PI)
    assert wrong_signs(rc, ["basic", "basic"], maximize=True) == []
    assert wrong_signs([0.0, -2.0, 1.0], ["basic", "lower", "upper"], maximize=True) == []


def test_a_minimization_flips_the_sign_rules():
    assert wrong_signs([0.0, -2.0, 1.0], ["basic", "lower", "upper"], maximize=False) == [1, 2]
    assert wrong_signs([0.0, 2.0, -1.0], ["basic", "lower", "upper"], maximize=False) == []


def test_a_basic_variable_needs_a_zero_reduced_cost():
    rc = reduced_costs(C, A, PI)
    assert wrong_signs(rc, ["basic", "basic", "basic"], maximize=True) == [2]
    assert wrong_signs([0.0, -0.3], ["basic", "basic"], maximize=True) == [1]
