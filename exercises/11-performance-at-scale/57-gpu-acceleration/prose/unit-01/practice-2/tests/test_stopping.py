import numpy as np

from stopping import converged

# a staffing LP: min 2 x1 + 3 x2  s.t.  x1 + x2 >= 4,  x1 + 2 x2 >= 6,  x >= 0
A = np.array([[1.0, 1.0], [1.0, 2.0]])
b = np.array([4.0, 6.0])
c = np.array([2.0, 3.0])
X, Y = np.array([2.0, 2.0]), np.array([1.0, 1.0])          # optimal: both rows tight, cost 10 = 4 + 6


def test_the_optimal_pair_passes_and_a_costlier_plan_fails():
    assert converged(A, b, c, X, Y, 1e-6)
    assert not converged(A, b, c, 1.5 * X, Y, 1e-6)


def test_a_nearly_optimal_pair_passes_a_loose_tolerance_and_fails_a_tight_one():
    x = X * (1 + 1e-7)
    assert converged(A, b, c, x, Y, 1e-4)
    assert not converged(A, b, c, x, Y, 1e-8)


def test_a_row_with_room_to_spare_is_not_a_breach():
    A3, b3 = np.vstack([A, [1.0, 0.0]]), np.append(b, 1.0)      # x1 >= 1 has room: x1 = 2
    assert converged(A3, b3, c, X, np.append(Y, 0.0), 1e-6)
    assert not converged(A3, b3, c, np.array([2.0, 1.0]), np.append(Y, 0.0), 1e-6)


def test_a_positive_reduced_cost_on_an_unused_variable_is_allowed():
    A3, c3 = np.hstack([A, [[1.0], [1.0]]]), np.append(c, 10.0)  # a third shift at 10, unused
    assert converged(A3, b, c3, np.append(X, 0.0), Y, 1e-6)
    assert not converged(A3, b, np.append(c, 1.0), np.append(X, 0.0), Y, 1e-6)


def test_scaling_the_units_keeps_the_verdict():
    s = 1e4                                                       # every need and every cost in smaller units
    x = X * (1 + 5e-7)
    assert converged(A, s * b, s * c, s * x, s * Y, 1e-6)
    assert not converged(A, s * b, s * c, s * 1.01 * X, s * Y, 1e-6)
