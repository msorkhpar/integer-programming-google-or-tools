import pytest
from ortools.math_opt.python import mathopt

from renewal import District, all_agree, relative_gap, solve_on

DISTRICTS = [
    District("North", 9, 4, 2, 10),
    District("South", 7, 3, 3, 8),
    District("East", 5, 2, 1, 12),
]
ORDERED = [District("North", 9, 4, 2, 10, min_km=6), DISTRICTS[1], DISTRICTS[2]]
SOLVERS = (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP)


def test_each_solver_reaches_the_optimum_within_its_tolerance():
    assert solve_on(DISTRICTS, 40, 30, mathopt.SolverType.GLOP) == pytest.approx(292 / 3, rel=1e-9)
    assert solve_on(DISTRICTS, 40, 30, mathopt.SolverType.HIGHS) == pytest.approx(292 / 3, rel=1e-9)
    assert solve_on(DISTRICTS, 40, 30, mathopt.SolverType.PDLP) == pytest.approx(292 / 3, rel=1e-5)


def test_the_three_solvers_agree_and_a_real_difference_is_caught():
    values = {s.name: solve_on(DISTRICTS, 40, 30, s) for s in SOLVERS}
    assert all_agree(values, 1e-4)
    assert not all_agree({"GLOP": 100.0, "HIGHS": 100.0, "PDLP": 101.0}, 1e-6)


def test_the_gap_is_relative_to_the_size_of_the_objective():
    assert relative_gap(2_000_000.0, 2_000_001.0) == pytest.approx(5e-7)
    assert all_agree({"GLOP": 2_000_000.0, "PDLP": 2_000_001.0}, 1e-6)


def test_near_zero_objectives_are_compared_against_one():
    assert relative_gap(0.0, 1e-9) == pytest.approx(1e-9)
    assert all_agree({"GLOP": 0.0, "PDLP": 1e-9}, 1e-6)


def test_a_solver_without_an_optimum_is_a_disagreement():
    assert solve_on(ORDERED, 40, 30, mathopt.SolverType.GLOP) is not None
    values = {s.name: solve_on(ORDERED, 20, 30, s) for s in SOLVERS}
    assert values == {"GLOP": None, "HIGHS": None, "PDLP": None}
    assert not all_agree({"GLOP": 50.0, "HIGHS": None, "PDLP": 50.0})
