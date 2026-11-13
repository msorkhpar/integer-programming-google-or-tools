import pyomo.environ as pyo
import pytest

from refurbish import DEPTHS, Pump, plan, value_points

# A water utility's pumps, not the lesson's portfolio. Horizon 3 years.
WEARING = [Pump("P1", 30, 3.2, 40, 500, 400), Pump("P2", 22, 2.6, 30, 800, 600),
           Pump("P3", 40, 4.0, 50, 300, 350)]
SLOW = [Pump("P4", 35, 1.4, 45, 3000, 300), Pump("P5", 50, 1.7, 60, 2000, 350)]
HORIZON = 3


def expected(pump, horizon=HORIZON):
    n = lambda a: ((a + horizon) / pump.eta) ** pump.beta - (a / pump.eta) ** pump.beta
    return [pump.cof * (n(pump.age) - n((1 - d) * pump.age)) for d in DEPTHS]


def pyomo_value(pumps, fund):
    """The same model written by Pyomo's Piecewise (incremental form), from the formula's points."""
    m = pyo.ConcreteModel()
    m.R = pyo.Set(initialize=[p.pid for p in pumps])
    m.d = pyo.Var(m.R, bounds=(0, 1))
    m.v = pyo.Var(m.R)
    m.curve = pyo.Piecewise(m.R, m.v, m.d, pw_pts={p.pid: list(DEPTHS) for p in pumps},
                            f_rule={p.pid: expected(p) for p in pumps}, pw_constr_type="EQ", pw_repn="INC")
    m.fund = pyo.Constraint(expr=sum(p.capex * m.d[p.pid] for p in pumps) <= fund)
    m.obj = pyo.Objective(expr=sum(m.v[i] for i in m.R), sense=pyo.maximize)
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    solver.solve(m)
    return pyo.value(m.obj)


def test_value_points_follow_the_failure_model():
    for pump in WEARING + SLOW:
        assert value_points(pump, HORIZON) == pytest.approx(expected(pump))
    assert value_points(WEARING[0], 6) == pytest.approx(expected(WEARING[0], 6))


def test_the_plan_matches_pyomo_for_wearing_out_pumps():
    value, depths = plan(WEARING, 700, HORIZON)
    assert value == pytest.approx(pyomo_value(WEARING, 700), abs=1e-4)
    assert sum(p.capex * depths[p.pid] for p in WEARING) <= 700 + 1e-6


def test_the_plan_matches_pyomo_with_slowly_ageing_pumps():
    fleet = WEARING + SLOW
    value, depths = plan(fleet, 900, HORIZON)
    assert value == pytest.approx(pyomo_value(fleet, 900), abs=1e-4)
    assert sum(p.capex * depths[p.pid] for p in fleet) <= 900 + 1e-6
