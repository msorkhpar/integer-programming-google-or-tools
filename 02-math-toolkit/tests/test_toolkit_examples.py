"""The module 02 examples compute what their lessons say they print."""

import numpy as np
import pytest


def test_value_and_cost_are_dot_products():
    from plan_vectors import capex, npv, to_vector
    x = to_vector({"P001", "P002", "P005", "P006"})
    assert capex @ x == 7100 and npv @ x == 3627


def test_the_one_period_best_plan_breaks_the_2028_budget():
    from budget_matrix import A, b
    x = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    assert A.shape == (3, 8)
    assert (A @ x).tolist() == [250, 5720, 1130]
    assert (A @ x <= b).tolist() == [True, False, True]


def test_a_tolerance_accepts_a_sum_that_misses_by_rounding():
    from tolerance import A, b, is_feasible, x
    assert not np.all(A @ x <= b)
    assert is_feasible(A, b, x)


def test_rules_in_leq_form_flag_the_broken_rows():
    from rules_matrix import full_model
    names, A, b = full_model()
    assert A.shape == (7, 8)
    x = np.array([1, 0, 1, 1, 0, 0, 0, 0])
    assert [n for n, ok in zip(names, A @ x <= b) if not ok] == ["budget_2028", "must_P002_ge"]


def test_one_product_checks_all_plans_and_finds_the_best():
    from all_plans import X, best, feasible, npv
    assert X.shape == (8, 256) and int(feasible.sum()) == 8
    assert best.tolist() == [0, 1, 0, 0, 1, 0, 1, 1] and npv @ best == 1396


def test_the_vectorized_check_agrees_with_a_loop():
    from all_plans import A, X, b, feasible
    looped = [all(A[i] @ X[:, k] <= b[i] for i in range(len(b))) for k in range(X.shape[1])]
    assert looped == feasible.tolist()


@pytest.mark.parametrize("size, nnz", [("tiny", 26), ("small", 122), ("medium", 1368), ("large", 34610)])
def test_model_matrix_nonzeros(size, nnz):
    from gridcap import generate
    from model_matrix import csr
    A, b, names = csr(generate(size))
    assert A.nnz == nnz and A.shape[0] == len(names) == len(b)


def test_csr_matches_dense_and_stores_far_less():
    from gridcap import generate
    from model_matrix import csr, stored_bytes
    A, b, names = csr(generate("medium"))
    dense = A.toarray()
    x = np.zeros(A.shape[1], dtype=int)
    x[::3] = 1
    assert np.array_equal(A @ x, dense @ x)
    assert stored_bytes(A) * 10 < dense.nbytes


def test_csr_row_reads_back_the_2028_budget():
    from csr_anatomy import names, rows, cols, vals, tiny
    from scipy import sparse
    A = sparse.coo_array((vals, (rows, cols)), shape=(len(names), 8)).tocsr()
    i = names.index("budget_2028")
    row = A.toarray()[i]
    assert row.tolist() == [2150, 2730, 1490, 2000, 0, 840, 0, 0]


def test_mathopt_stores_exactly_the_nonzeros():
    from mathopt_matrix import A, model
    matrix = model.export_model().linear_constraint_matrix
    assert len(matrix.coefficients) == A.nnz == 26


def test_the_polygon_has_five_vertices_and_glop_finds_the_best():
    from vertices import corners
    found = [p for _, _, p, kind in corners() if kind == "vertex"]
    assert sorted(tuple(p.tolist()) for p in found) == [(500, 0), (500, 1500), (1000, 1500), (2000, 1000), (3000, 0)]
    assert sum(1 for *_, kind in corners() if kind == "parallel") == 1


def test_points_on_a_segment_between_feasible_points_stay_feasible():
    from polygon import is_feasible
    p, q = np.array([500, 0]), np.array([1000, 1500])
    assert all(is_feasible((1 - t) * p + t * q) for t in np.linspace(0, 1, 21))


def test_the_midpoint_of_two_plans_is_feasible_but_not_a_plan_and_the_lp_is_fractional():
    from not_convex import A, X, b, feasible, lp_relaxation
    plans = X[:, feasible]
    mid = (plans[:, 1] + plans[:, 2]) / 2
    assert np.all(A @ mid <= b) and not np.all((mid == 0) | (mid == 1))
    status, value, values = lp_relaxation()
    assert status == "OPTIMAL" and value == pytest.approx(2039.0, abs=0.05)
    assert 0 < values["P006"] < 1 and value > 1396


def test_rank_counts_independent_rows_and_an_empty_matrix_has_rank_zero():
    from independence import rows
    from polygon import A, b
    assert np.linalg.matrix_rank(rows) == 2 and np.linalg.matrix_rank(rows[:2]) == 2
    tight = np.abs(A @ np.array([2000, 1000]) - b) <= 1e-9
    assert np.linalg.matrix_rank(A[tight]) == 2
    inside = np.abs(A @ np.array([1000, 500]) - b) <= 1e-9
    assert A[inside].shape == (0, 2) and np.linalg.matrix_rank(A[inside]) == 0


def test_the_or_tools_lp_example_is_solved_at_its_best_vertex():
    from lp_example import c, solve_with_glop, vertices
    status, value, x, y = solve_with_glop()
    assert status == "OPTIMAL" and value == pytest.approx(34)
    assert (x, y) == (pytest.approx(6), pytest.approx(4))
    found = vertices()
    assert len(found) == 4
    assert max(float(c @ p) for p, _ in found) == pytest.approx(value)
    assert dict((tuple(p.round().tolist()), t) for p, t in found)[(0.0, 0.0)] == ["c2", "x_nonneg", "y_nonneg"]


def test_the_must_do_project_is_a_bound_in_the_mathopt_model():
    from mathopt_matrix import model, x
    from gridcap import generate
    must = [j for j, p in enumerate(generate("tiny").projects) if p.must_do]
    assert must and all(x[j].lower_bound == 1 for j in must)
    assert len(list(model.linear_constraints())) == 17
