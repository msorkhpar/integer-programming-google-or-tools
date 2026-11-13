import random

import pytest
from ortools.math_opt.python import mathopt

from methods import run_method

Algo = mathopt.LPAlgorithm


@pytest.fixture(scope="module")
def model():
    """A random 40-variable, 20-row packing LP: big enough that no presolve solves it outright."""
    rng = random.Random(7)
    m = mathopt.Model(name="packing")
    x = [m.add_variable(lb=0, ub=rng.randint(2, 9), name=f"x{j}") for j in range(40)]
    for i in range(20):
        m.add_linear_constraint(sum(rng.randint(1, 9) * x[j] for j in rng.sample(range(40), 12)) <= rng.randint(40, 90),
                                name=f"row{i}")
    m.maximize(sum(rng.randint(1, 20) * v for v in x))
    return m


def test_a_simplex_solve_counts_simplex_iterations(model):
    status, iterations = run_method(model, mathopt.SolverType.GLOP, Algo.DUAL_SIMPLEX)
    assert status == "OPTIMAL" and iterations > 0


def test_a_barrier_solve_counts_barrier_iterations(model):
    status, iterations = run_method(model, mathopt.SolverType.HIGHS, Algo.BARRIER)
    assert status == "OPTIMAL" and iterations > 0


def test_a_first_order_solve_counts_first_order_iterations(model):
    status, iterations = run_method(model, mathopt.SolverType.PDLP, Algo.FIRST_ORDER)
    assert status == "OPTIMAL" and iterations > 0


def test_an_algorithm_the_solver_lacks_is_refused_not_replaced(model):
    assert run_method(model, mathopt.SolverType.GLOP, Algo.DUAL_SIMPLEX)[0] == "OPTIMAL"
    assert run_method(model, mathopt.SolverType.GLOP, Algo.BARRIER) == ("REFUSED", 0)
    assert run_method(model, mathopt.SolverType.PDLP, Algo.PRIMAL_SIMPLEX) == ("REFUSED", 0)
