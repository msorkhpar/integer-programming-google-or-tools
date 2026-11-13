import pytest
from ortools.math_opt.python import mathopt

from prices import binding_prices

S = mathopt.SolverType


def dairy(integer: bool = False, bottled_value: float = 4.0):
    """Thousand litres to cheese, butter and bottled milk in one week of a co-op's plant."""
    model = mathopt.Model(name="dairy")
    c = model.add_variable(lb=0, ub=60, is_integer=integer, name="cheese")
    b = model.add_variable(lb=0, ub=60, is_integer=integer, name="butter")
    m = model.add_variable(lb=0, ub=60, is_integer=integer, name="bottled")
    rows = [
        model.add_linear_constraint(c + b + m <= 90, name="milk"),
        model.add_linear_constraint(3 * c + 2 * b + m <= 170, name="hours"),
        model.add_linear_constraint(m >= 30, name="contract"),
        model.add_linear_constraint(b <= 50, name="churn"),
    ]
    model.maximize(9 * c + 6 * b + bottled_value * m)
    return model, rows


def test_binding_rows_are_priced_and_rows_with_slack_are_left_out():
    model, rows = dairy()
    prices = binding_prices(mathopt.solve(model, S.GLOP), rows)
    assert set(prices) == {"milk", "hours"}
    assert prices["milk"] == pytest.approx(1.5)
    assert prices["hours"] == pytest.approx(2.5)


def test_a_result_without_duals_gives_none():
    model, rows = dairy(integer=True)
    assert binding_prices(mathopt.solve(model, S.HIGHS), rows) is None


def test_a_row_tight_at_its_lower_bound_is_binding():
    model, rows = dairy(bottled_value=2.0)       # bottled milk now earns less: only the contract keeps it
    prices = binding_prices(mathopt.solve(model, S.GLOP), rows)
    assert set(prices) == {"hours", "contract"}
    assert prices["contract"] == pytest.approx(-1.0)


def test_a_pdlp_result_without_a_basis_is_priced_too():
    model, rows = dairy()
    result = mathopt.solve(model, S.PDLP)
    assert not result.has_basis()
    prices = binding_prices(result, rows, tol=1e-3)
    assert set(prices) == {"milk", "hours"}
    assert prices["hours"] == pytest.approx(2.5, abs=1e-3)
