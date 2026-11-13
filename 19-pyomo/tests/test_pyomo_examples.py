"""The module 19 examples: the Pyomo port agrees with the MathOpt models of section 6, and each tool behaves as the lessons say."""

import importlib.util
import sys
from pathlib import Path

import pyomo.environ as pyo
import pytest
from ortools.math_opt.python import mathopt
from pyomo.contrib.piecewise import PiecewiseLinearFunction
from pyomo.contrib.solver.common.factory import SolverFactory

import contractor_model
import outage_gdp
import pyomo_timing
from gridcap import generate
from iis_tools import cut, explain, mis_lines

COURSE = Path(__file__).resolve().parents[2]


def section_6(module: str, name: str):
    """Load a section 6 MathOpt model from its own module, under a name that cannot clash."""
    spec = importlib.util.spec_from_file_location(f"s6_{name}", COURSE / module / "src" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


timing_model = section_6("26-multi-period-timing", "timing_model")
outage_model = section_6("24-big-m-and-indicators", "outage_model")
EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
OUTAGE = ("P011", "P016", "P021")


@pytest.fixture(scope="module")
def small():
    return generate("small")


def pyomo_value(m):
    SolverFactory("highs").solve(m, rel_gap=0.0)
    return pyo.value(m.value)


@pytest.mark.parametrize("size", ["tiny", "small"])
@pytest.mark.parametrize("integer", [True, False])
def test_the_port_has_the_mathopt_optimum_and_size(size, integer):
    portfolio = generate(size)
    tm = timing_model.build(portfolio, integer=integer)
    reference = timing_model.solve_highs(tm.model, EXACT)
    m = pyomo_timing.build(portfolio, integer=integer)
    assert pyomo_value(m) == pytest.approx(reference.objective_value(), abs=1e-6)
    assert len(m.x) == tm.model.get_num_variables()
    assert m.nconstraints() == tm.model.get_num_linear_constraints()


def test_the_port_finds_lesson_6_4_1s_schedule(small):
    m = pyomo_timing.build(small)
    pyomo_timing.highs().solve(m)
    tm = timing_model.build(small)
    assert pyomo_timing.schedule(m) == timing_model.schedule(tm, timing_model.solve_highs(tm.model, EXACT))


def test_a_mutable_budget_reaches_the_row_without_a_rebuild(small):
    m = pyomo_timing.build(small)
    m.budget[2030] = 4000
    rebuilt = timing_model.build(small)
    rebuilt.model.delete_linear_constraint(rebuilt.budget[2030])
    rebuilt.model.add_linear_constraint(rebuilt.spend[2030] <= 4000)
    assert pyomo_value(m) == pytest.approx(timing_model.solve_highs(rebuilt.model, EXACT).objective_value())


def outage_bounds(small, form):
    durations = {pid: small.project(pid).crew_months for pid in OUTAGE}
    m = outage_gdp.build(durations, 12)
    pyo.TransformationFactory(form).apply_to(m)
    pyomo_timing.highs().solve(m)
    best = pyo.value(m.finish)
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)
    pyomo_timing.highs().solve(m)
    return pyo.value(m.finish), best


@pytest.mark.parametrize("form,hand", [("gdp.bigm", "big_m"), ("gdp.hull", "hull")])
def test_gdp_transformations_give_lesson_6_2_4s_bounds(small, form, hand):
    durations = {pid: small.project(pid).crew_months for pid in OUTAGE}
    lp = outage_model.build(durations, 12, hand, integer=False)
    milp = outage_model.build(durations, 12, hand)
    bound, best = outage_bounds(small, form)
    assert bound == pytest.approx(mathopt.solve(lp.model, mathopt.SolverType.GLOP).objective_value(), abs=1e-6)
    assert best == pytest.approx(mathopt.solve(milp.model, mathopt.SolverType.HIGHS).objective_value(), abs=1e-6)
    assert best == pytest.approx(17)


def test_hull_is_tighter_than_big_m_here(small):
    assert outage_bounds(small, "gdp.hull")[0] > outage_bounds(small, "gdp.bigm")[0] + 3


def contractor(small, **kwargs):
    m = contractor_model.build(small, 40, **kwargs)
    pyomo_timing.highs().solve(m)
    return m


@pytest.mark.parametrize("kwargs", [dict(repn="SOS2"), dict(repn="INC", force_pw=True), dict(constr_type="EQ"),
                                    dict(repn="CC", force_pw=True), dict(repn="DCC", force_pw=True)])
def test_every_exact_form_of_the_rising_tiers_agrees(small, kwargs):
    m = contractor(small, **kwargs)
    assert pyo.value(m.net) == pytest.approx(24839)
    assert m.contract.value == pytest.approx(contractor_model.tier_cost(m.bought.value), abs=1e-6)


def test_convex_lb_needs_no_binaries_and_sos2_is_refused_when_written(small):
    shortcut = contractor_model.build(small, 40, repn="SOS2")
    assert not any(v.is_binary() for v in shortcut.tiers.component_data_objects(pyo.Var))
    with pytest.raises(NotImplementedError):
        contractor(small, repn="SOS2", force_pw=True)
    with pytest.raises(NotImplementedError):
        contractor(small, cost=contractor_model.DISCOUNT, repn="SOS2")


def test_a_discount_needs_lb_with_binaries_and_ub_is_wrong(small):
    right = contractor(small, cost=contractor_model.DISCOUNT)
    assert right.contract.value == pytest.approx(contractor_model.tier_cost(right.bought.value, contractor_model.DISCOUNT))
    wrong = contractor(small, cost=contractor_model.DISCOUNT, constr_type="UB")
    assert wrong.contract.value == pytest.approx(0) and wrong.bought.value == pytest.approx(40)


def test_contrib_piecewise_agrees(small):
    m = contractor_model.build(small, 40)
    m.tiers.deactivate()
    m.price = PiecewiseLinearFunction(tabular_data=dict(zip(contractor_model.MONTHS, contractor_model.COST)))
    m.pay = pyo.Constraint(expr=m.contract >= m.price(m.bought))
    pyo.TransformationFactory("contrib.piecewise.incremental").apply_to(m)
    pyomo_timing.highs().solve(m)
    assert pyo.value(m.net) == pytest.approx(24839)


def test_fixed_integer_duals_price_contractor_months(small):
    m = contractor(small)
    for v in m.x.values():
        v.fix(round(v.value))
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)
    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    pyomo_timing.highs().solve(m)
    assert m.dual[m.crews] == pytest.approx(70)       # the third tier's price, $k a month
    assert m.dual[m.budget] == pytest.approx(0)


def test_a_milp_returns_no_duals(small):
    m = pyomo_timing.build(small)
    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    with pytest.raises(RuntimeError):
        pyomo_timing.highs().solve(m)


def test_the_mis_names_the_budget_rows_and_the_two_must_dos():
    rows = [line for line in mis_lines(explain(cut(2600))) if line.startswith("constraint")]
    assert sorted(rows) == ["constraint: once[P010]", "constraint: once[P017]",
                            "constraint: spend_cap[2030]", "constraint: spend_cap[2031]"]


def test_the_mis_tool_cannot_see_an_integer_only_conflict():
    m = cut(4000)
    assert not pyo.check_optimal_termination(pyomo_timing.highs().solve(m, load_solutions=False))
    with pytest.raises(Exception, match="to be feasible"):
        explain(m)
