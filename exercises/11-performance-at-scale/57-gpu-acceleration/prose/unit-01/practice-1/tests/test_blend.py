import numpy as np

from blend import pdhg_step, solve

# min x1 + 2 x2  s.t.  x1 + x2 = 4,  0 <= x <= 3
A1, b1, c1, u1 = np.array([[1.0, 1.0]]), np.array([4.0]), np.array([1.0, 2.0]), np.array([3.0, 3.0])

# a feed blend: cost per tonne of three ingredients, two nutrient rows met exactly, at most 10 t each
BLEND_A = np.array([[2.0, 1.0, 1.0], [1.0, 3.0, 2.0]])
BLEND_b = np.array([8.0, 12.0])
BLEND_c = np.array([3.0, 4.0, 2.5])
BLEND_u = np.array([10.0, 10.0, 10.0])
BLEND_OPTIMUM = 52.0 / 3.0


def test_the_optimal_pair_is_a_fixed_point_and_another_pair_moves():
    A2, b2, u2 = np.array([[1.0, 1.0], [1.0, 3.0]]), np.array([4.0, 6.0]), np.array([10.0, 10.0])
    x, y = pdhg_step(A2, b2, c1, u2, np.array([3.0, 1.0]), np.array([0.5, 0.5]), 0.1, 0.1)   # optimal pair
    assert np.allclose(x, [3.0, 1.0]) and np.allclose(y, [0.5, 0.5])
    x, y = pdhg_step(A1, b1, c1, u1, np.array([1.0, 1.0]), np.array([0.0]), 0.1, 0.1)
    assert np.allclose(x, [0.9, 0.8]) and np.allclose(y, [0.1 * (4.0 - 1.4)])


def test_the_iterations_reach_the_blend_optimum():
    x, y = solve(BLEND_A, BLEND_b, BLEND_c, BLEND_u, 20_000)
    assert abs(BLEND_c @ x - BLEND_OPTIMUM) <= 1e-4 * BLEND_OPTIMUM
    assert np.max(np.abs(BLEND_A @ x - BLEND_b)) <= 1e-4


def test_an_exact_row_can_take_a_negative_price():
    A, b, c, u = np.array([[1.0]]), np.array([1.0]), np.array([0.0]), np.array([5.0])
    x, y = pdhg_step(A, b, c, u, np.array([3.0]), np.array([0.0]), 0.5, 0.5)
    assert np.allclose(x, [3.0])
    assert np.allclose(y, [-1.0])


def test_the_price_step_looks_ahead():
    A, b, c, u = np.array([[1.0]]), np.array([2.0]), np.array([1.0]), np.array([5.0])
    x, y = pdhg_step(A, b, c, u, np.array([1.0]), np.array([0.0]), 0.5, 0.5)
    assert np.allclose(x, [0.5])
    assert np.allclose(y, [0.5 * (2.0 - 0.0)])


def test_a_variable_never_passes_its_upper_bound():
    A, b, c, u = np.array([[1.0]]), np.array([1.0]), np.array([-4.0]), np.array([2.0])
    x, y = pdhg_step(A, b, c, u, np.array([1.5]), np.array([0.0]), 0.5, 0.1)
    assert np.allclose(x, [2.0])
    assert np.allclose(y, [0.1 * (1.0 - 2.5)])
