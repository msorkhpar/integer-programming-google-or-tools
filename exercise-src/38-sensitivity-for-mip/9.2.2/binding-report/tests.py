import pytest
from ortools.math_opt.python import mathopt

from rows import row_report


def solve(model):
    return mathopt.solve(model, mathopt.SolverType.GLOP)


def test_a_full_row_binds_and_a_loose_row_does_not():
    m = mathopt.Model()
    chlorine = m.add_variable(lb=0, name="chlorine")
    ozone = m.add_variable(lb=0, name="ozone")
    m.add_linear_constraint(chlorine + ozone <= 50, name="stock")
    m.add_linear_constraint(chlorine + 2 * ozone <= 200, name="mixer_hours")
    m.maximize(3 * chlorine + 2 * ozone)
    report = row_report(m, solve(m))
    assert report["stock"]["binding"] is True
    assert report["stock"]["price"] == pytest.approx(3)
    assert report["mixer_hours"]["binding"] is False
    assert report["mixer_hours"]["slack"] == pytest.approx(150)


def test_a_binding_row_with_a_zero_price_is_still_binding():
    # The spare pump is out of service (spare <= 0). Its flow earns nothing, so the row's price is
    # 0, yet the flow sits exactly at the row's limit.
    m = mathopt.Model()
    main = m.add_variable(lb=0, ub=30, name="main_flow")
    spare = m.add_variable(lb=0, name="spare_flow")
    m.add_linear_constraint(spare <= 0, name="spare_out_of_service")
    m.maximize(main)
    report = row_report(m, solve(m))
    assert report["spare_out_of_service"]["price"] == pytest.approx(0)
    assert report["spare_out_of_service"]["binding"] is True


def test_a_greater_or_equal_row_measures_slack_from_its_lower_bound():
    m = mathopt.Model()
    dose = m.add_variable(lb=0, ub=100, name="dose")
    m.add_linear_constraint(dose >= 12, name="disinfection")
    m.minimize(dose)
    report = row_report(m, solve(m))
    assert report["disinfection"]["slack"] == pytest.approx(0)
    assert report["disinfection"]["binding"] is True


def test_a_row_within_float_noise_of_its_bound_binds():
    m = mathopt.Model()
    dose = m.add_variable(lb=0, name="dose")
    m.add_linear_constraint(0.1 * dose <= 0.3, name="residual")
    m.add_linear_constraint(dose <= 3.0000000001, name="pump_rate")
    m.maximize(dose)
    report = row_report(m, solve(m))
    assert report["residual"]["binding"] is True
    assert report["pump_rate"]["binding"] is True
