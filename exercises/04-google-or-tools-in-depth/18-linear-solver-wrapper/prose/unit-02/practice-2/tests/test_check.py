from ortools.linear_solver import pywraplp

from check import allowed


def model():
    """Pumps p (integer, 0..5) and hours h (0..30): 10 <= 4p + h <= 28, and p + h <= 20."""
    solver = pywraplp.Solver.CreateSolver("SCIP")
    p = solver.IntVar(0, 5, "p")
    h = solver.NumVar(0, 30, "h")
    band = solver.RowConstraint(10, 28, "band")
    band.SetCoefficient(p, 4)
    band.SetCoefficient(h, 1)
    solver.Add(p + h <= 20, "total")
    return solver


def test_a_plan_inside_every_row_is_allowed_and_one_over_a_row_is_refused():
    assert allowed(model(), {"p": 3, "h": 10.0}) is True       # 22 in [10, 28]; 13 <= 20
    assert allowed(model(), {"p": 5, "h": 16.0}) is False      # band 36 > 28


def test_a_row_below_its_lower_bound_is_refused():
    assert allowed(model(), {"p": 3, "h": 10.0}) is True
    assert allowed(model(), {"p": 1, "h": 2.0}) is False       # band 6 < 10


def test_a_variable_outside_its_bounds_is_refused():
    assert allowed(model(), {"p": 3, "h": 10.0}) is True
    assert allowed(model(), {"p": 6, "h": 0.0}) is False       # rows hold (band 24, total 6), but p > 5


def test_an_integer_variable_with_a_fraction_is_refused():
    assert allowed(model(), {"p": 3, "h": 10.0}) is True
    assert allowed(model(), {"p": 2.5, "h": 5.0}) is False     # rows hold (band 15, total 7.5), but p is not whole


def test_a_row_missed_by_rounding_noise_is_allowed():
    assert allowed(model(), {"p": 3, "h": 16.0000000005}) is True   # band 28.0000000005: noise
    assert allowed(model(), {"p": 3, "h": 17.0}) is False           # band 29 > 28
