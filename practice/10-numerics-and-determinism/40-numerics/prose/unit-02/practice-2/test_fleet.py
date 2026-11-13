import pytest
from ortools.math_opt.python import mathopt

from fleet import build_scaled


def matrix_span(model: mathopt.Model) -> float:
    sizes = [abs(row.get_coefficient(v)) for row in model.linear_constraints() for v in model.row_nonzeros(row)]
    return max(sizes) / min(sizes)


def fixed(orders: set[str], overdraft_k: float, arranged: int) -> mathopt.SolveResult:
    fleet = build_scaled()
    for name, var in fleet.buy.items():
        var.lower_bound = var.upper_bound = 1.0 if name in orders else 0.0
    fleet.overdraft.lower_bound = fleet.overdraft.upper_bound = overdraft_k
    fleet.arranged.lower_bound = fleet.arranged.upper_bound = float(arranged)
    return mathopt.solve(fleet.model, mathopt.SolverType.HIGHS)


def allowed(orders: set[str], overdraft_k: float, arranged: int) -> bool:
    return fixed(orders, overdraft_k, arranged).has_primal_feasible_solution()


def test_an_overdraft_needs_its_arrangement_and_a_plan_without_one_is_refused():
    assert allowed({"electric", "hybrid", "shuttle"}, 250, 1) is True
    assert allowed({"electric", "hybrid", "shuttle"}, 250, 0) is False


def test_the_matrix_span_shrinks_below_ten_thousand():
    assert matrix_span(build_scaled().model) < 1e4


def test_the_overdraft_limit_is_converted_too():
    assert allowed({"electric", "hybrid", "shuttle"}, 900, 1) is True
    assert allowed({"electric", "hybrid", "diesel"}, 1300, 1) is False


def test_the_objective_is_in_k():
    result = fixed({"electric", "hybrid", "shuttle"}, 250, 1)
    assert result.has_primal_feasible_solution()
    assert result.objective_value() == pytest.approx(8_470)
