import pyomo.environ as pyo
import pytest

from report import outcome

# Small crew-rostering models, not the lesson's portfolio.


def roster(shifts_needed, integer=True):
    m = pyo.ConcreteModel()
    m.S = pyo.Set(initialize=["day", "night", "weekend"])
    pay = {"day": 3, "night": 4, "weekend": 5}
    m.crew = pyo.Var(m.S, domain=pyo.NonNegativeIntegers if integer else pyo.NonNegativeReals, bounds=(0, 6))
    m.cover = pyo.Constraint(expr=sum(m.crew[s] for s in m.S) >= shifts_needed)
    m.nights = pyo.Constraint(expr=m.crew["night"] >= 2)
    m.cost = pyo.Objective(expr=sum(pay[s] * m.crew[s] for s in m.S))
    return m


def run(model, **options):
    try:
        return outcome(model, **options)
    except Exception as error:
        raise AssertionError(f"outcome raised {type(error).__name__}: {error}") from None


def test_an_optimal_roster_reports_its_cost_and_plan():
    found = run(roster(9))
    assert found["status"] == "optimal"
    assert found["objective"] == pytest.approx(30)
    assert found["plan"]["crew[day]"] == pytest.approx(6) and found["plan"]["crew[night]"] == pytest.approx(3)


def test_an_impossible_roster_is_infeasible_with_no_plan():
    found = run(roster(25))
    assert found["status"] == "infeasible"
    assert found["objective"] is None and found["plan"] == {}


def test_an_unbounded_milp_is_not_called_infeasible():
    m = roster(9)
    m.bonus = pyo.Var(domain=pyo.NonNegativeIntegers)
    m.cost.expr = m.cost.expr - m.bonus
    found = run(m)
    assert found["status"] == "infeasible or unbounded"
    assert found["objective"] is None and found["plan"] == {}
