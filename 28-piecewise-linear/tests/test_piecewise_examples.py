"""The module 28 examples: convex curves without binaries, the lambda, incremental and log forms, and value curves."""

import itertools

import pytest
from ortools.math_opt.python import mathopt

from adjacent_weights import y_range
from credit_exact import weights_only
from credit_line import FALLING, RISING, with_credit
from direction_table import pushed
from gridcap import generate
from lifecycle import candidates, renewal_model, risk_avoided, by_shape, value_curve
from log_codes import weighted
from medium_discounts import with_discounts
from piecewise import FORMS, Curve, add_epigraph, add_incremental, add_lambda, add_segments, gray, log_sets, value
from renewal_plan import FUND
from selection import EXACT, funded, solve_highs


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(model):
    result = solve_highs(model, EXACT)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    return result


def test_the_curve_interpolates_and_knows_its_shape():
    assert RISING(2000) == pytest.approx(275)
    assert FALLING(4500) == pytest.approx(1200)
    assert RISING.convex() and not RISING.concave()
    assert FALLING.concave() and not FALLING.convex()


@pytest.mark.parametrize("form", [add_segments, add_epigraph])
def test_rising_tiers_need_no_binaries_and_fill_in_order(small, form):
    sel, loan = with_credit(small, RISING, form)
    result = solve(sel.model)
    assert result.objective_value() == pytest.approx(26_686)
    assert value(result, loan.x) == pytest.approx(3_600)
    assert sum(v.integer for v in sel.model.variables()) == len(small.projects)
    if form is add_segments:
        assert [result.variable_values(d) for d in loan.parts["delta"]] == pytest.approx([1500, 1500, 600])


def test_falling_tiers_as_segments_claim_a_cost_the_line_does_not_charge(small):
    sel, loan = with_credit(small, FALLING, add_segments)
    result = solve(sel.model)
    npv = sum(small.project(i).value for i in funded(sel, result))
    assert result.objective_value() == pytest.approx(26_861)
    assert npv - result.objective_value() == pytest.approx(620)
    assert FALLING(value(result, loan.x)) == pytest.approx(1_110)


@pytest.mark.parametrize("curve, push, exact", [(RISING, "down", True), (RISING, "up", False),
                                                 (FALLING, "down", False), (FALLING, "up", True)])
def test_segments_are_exact_only_when_the_push_matches_the_shape(curve, push, exact):
    got = [pushed(curve, x, push) for x in (1000, 2000, 3500, 4500)]
    assert all(abs(g - curve(x)) < 1e-6 for g, x in zip(got, (1000, 2000, 3500, 4500))) is exact


def test_segment_binaries_pin_y_and_weights_alone_do_not():
    assert y_range(FALLING, 2000, False) == "500 to 800"
    assert y_range(FALLING, 2000, True) == "800"


def test_the_lambda_form_solves_the_falling_tiers_exactly(small):
    sel, loan = with_credit(small, FALLING, add_lambda)
    result = solve(sel.model)
    assert result.objective_value() == pytest.approx(26_753)
    assert value(result, loan.x) == pytest.approx(4_900)
    lam = [result.variable_values(v) for v in loan.parts["lam"]]
    nonzero = [j for j, v in enumerate(lam) if v > 1e-6]
    assert len(nonzero) <= 2 and (len(nonzero) < 2 or nonzero[1] == nonzero[0] + 1)
    sel, loan = with_credit(small, FALLING, weights_only)
    assert solve(sel.model).objective_value() == pytest.approx(26_768)


def test_the_three_forms_agree_and_share_one_lp_bound(small):
    values = set()
    for form in FORMS.values():
        sel, _ = with_credit(small, FALLING, form)
        values.add(round(solve(sel.model).objective_value(), 3))
        for v in sel.model.variables():
            v.integer = False
        values.add(round(solve(sel.model).objective_value(), 1))
    assert values == {26_753.0, 26_959.1}


@pytest.mark.parametrize("K", range(2, 7))
def test_every_log_code_allows_exactly_one_segment(K):
    n = len(log_sets(K))
    used = {tuple(gray(s) >> b & 1 for b in range(n)): s for s in range(K)}
    for bits in itertools.product((0, 1), repeat=n):
        assert weighted(K, bits) == ([used[bits], used[bits] + 1] if bits in used else [])


@pytest.mark.parametrize("form", list(FORMS.values()))
def test_any_curve_is_exact_at_every_point_with_each_form(form):
    curve = Curve((0.0, 2.0, 3.0, 5.0, 6.0), (0.0, 4.0, 1.0, 5.0, 2.0))
    for x in (0.5, 2.0, 2.5, 4.0, 5.5):
        for sense in ("min", "max"):
            model = mathopt.Model()
            piece = form(model, curve, "c")
            model.add_linear_constraint(piece.x == x)
            model.minimize(piece.y) if sense == "min" else model.maximize(piece.y)
            assert solve(model).objective_value() == pytest.approx(curve(x))


def test_medium_discounts_with_four_tiers():
    sel, binaries = with_discounts(generate("medium"), 4, FORMS["incremental"])
    assert binaries == 9
    assert solve(sel.model).objective_value() == pytest.approx(203_664)


def test_value_curves_are_concave_exactly_for_wearing_out_assets(small):
    for p, a in candidates(small):
        curve = value_curve(a)
        assert curve.concave() == (a.weibull_beta > 2)
        assert curve.convex() == (a.weibull_beta < 2)
        assert curve.ys[0] == 0 and curve.ys[-1] == pytest.approx(risk_avoided(a, 1.0))


def test_the_renewal_plan_by_shape_matches_the_incremental_plan(small):
    claims = {}
    for label, choose in (("segments", lambda c: add_segments), ("incremental", lambda c: add_incremental),
                          ("shape", by_shape)):
        plan = renewal_model(small, FUND, choose)
        claims[label] = solve(plan.model).objective_value()
    assert claims["segments"] == pytest.approx(2_971.0, abs=0.05)
    assert claims["incremental"] == pytest.approx(2_926.5, abs=0.05)
    assert claims["shape"] == pytest.approx(claims["incremental"])


def test_pyomo_piecewise_agrees_with_mathopt(small):
    pyo = pytest.importorskip("pyomo.environ")
    from pyomo_check import pyomo_renewal
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    m = pyomo_renewal(small, FUND, "INC")
    solver.solve(m)
    assert pyo.value(m.obj) == pytest.approx(2_926.5, abs=0.05)


def test_cpsat_element_agrees_with_mathopt_on_quarter_depths(small):
    from cpsat_element import cpsat, mathopt_quarters
    status, best, quarters = cpsat(small)
    assert status == "OPTIMAL"
    assert (best, quarters) == (mathopt_quarters(small)[0], mathopt_quarters(small)[1])
