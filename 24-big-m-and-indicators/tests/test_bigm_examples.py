"""The module 24 examples: big-M values, LP bounds, tolerance leaks, indicators, CP-SAT and disjunctions."""

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_model import (build, hired, m_by_solving, m_from_once_rows, m_from_variable_bounds,
                        quiet_solve)
from outage_model import build as build_outage

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def ms(small):
    return {"bounds": m_from_variable_bounds(small), "once": m_from_once_rows(small),
            "lp": m_by_solving(small, integer=False), "milp": m_by_solving(small, integer=True)}


def test_each_way_to_get_m_is_at_most_the_one_before(ms):
    for key in ms["bounds"]:
        assert ms["bounds"][key] >= ms["once"][key] >= ms["lp"][key] >= ms["milp"][key] >= 0


def test_the_tightest_m_is_valid_and_one_less_refuses_a_plan():
    tiny = generate("tiny")
    row = ("distribution", 2029)

    def allows(big_m):
        cm = build(tiny, {key: 100 for key in tiny.crews} | {row: big_m})
        plan = {"P002": 2028, "P001": 2029}
        for (pid, t), var in cm.x.items():
            var.lower_bound = var.upper_bound = 1.0 if plan.get(pid) == t else 0.0
        cm.hire[row].lower_bound = 1.0
        return quiet_solve(cm.model).termination.reason == mathopt.TerminationReason.OPTIMAL

    assert m_by_solving(tiny, integer=True)[row] == 2
    assert allows(2) and not allows(1)


def test_every_valid_m_gives_the_same_milp_and_tighter_m_a_lower_lp_bound(small, ms):
    lp = {name: mathopt.solve(build(small, m, integer=False).model, mathopt.SolverType.GLOP).objective_value()
          for name, m in [("1e6", 1e6)] + list(ms.items())}
    assert lp["1e6"] >= lp["bounds"] >= lp["once"] >= lp["lp"] >= lp["milp"] - 1e-6
    assert lp["1e6"] > lp["milp"] + 100
    values = {name: quiet_solve(build(small, m).model, params=EXACT).objective_value()
              for name, m in [("1e6", 1e6), ("milp", ms["milp"])]}
    assert values["1e6"] == pytest.approx(values["milp"])


def test_a_huge_m_without_presolve_returns_a_plan_that_breaks_the_crew_rule(small):
    cm = build(small, 1e7)
    result = quiet_solve(cm.model, params=mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF))
    values = result.variable_values()
    leaks = [key for key, h in cm.hire.items()
             if values[h] < 0.5 and mathopt.evaluate_expression(cm.use[key], values) > small.crews[key] + 1e-6]
    assert leaks


def test_indicator_big_m_and_cp_sat_agree(small, ms):
    big = quiet_solve(build(small, ms["milp"]).model, params=EXACT)
    ind = build(small, None, form="indicator")
    scip = quiet_solve(ind.model, mathopt.SolverType.GSCIP, params=EXACT)
    assert scip.objective_value() == pytest.approx(big.objective_value())
    assert hired(ind, scip)
    with pytest.raises(Exception):
        quiet_solve(ind.model, mathopt.SolverType.HIGHS)


def test_the_hull_bound_is_tighter_and_the_orders_agree():
    durations = {"P011": 2, "P016": 3, "P021": 5}
    lp = {f: mathopt.solve(build_outage(durations, 12, f, integer=False).model, mathopt.SolverType.GLOP).objective_value()
          for f in ("big_m", "hull")}
    milp = {f: mathopt.solve(build_outage(durations, 12, f).model, mathopt.SolverType.HIGHS).objective_value()
            for f in ("big_m", "hull")}
    assert lp["big_m"] == pytest.approx(sum(durations.values()))
    assert lp["big_m"] < lp["hull"] <= milp["hull"] + 1e-6
    assert milp["big_m"] == pytest.approx(milp["hull"]) == pytest.approx(17)


@pytest.mark.parametrize("big_m, bound", [(None, 3.7), (370, 1.0), (1e6, 370 / 1e6)])
def test_bin_packing_needs_4_bins_and_a_looser_m_weakens_the_lp(big_m, bound):
    from bin_packing_m import bin_packing
    lp = quiet_solve(bin_packing(big_m, integer=False), mathopt.SolverType.GLOP)
    assert lp.objective_value() == pytest.approx(bound, abs=1e-6)
    assert quiet_solve(bin_packing(big_m), mathopt.SolverType.HIGHS).objective_value() == pytest.approx(4)


def test_scip_refuses_equality_indicators_and_one_sided_ones_match_cpsat():
    from if_then_else import cpsat_table, indicator_model, scip_table
    model, *_ = indicator_model(one_sided=False)
    with pytest.raises(Exception) as error:
        quiet_solve(model, mathopt.SolverType.GSCIP)
    assert "ranged implied constraints" in str(error.value.__context__)
    expected = [(x, 0 if x < 5 else 10 - x, int(x >= 5)) for x in range(11)]
    assert cpsat_table() == expected
    assert scip_table() == expected


def test_glop_refuses_a_relaxed_indicator_model(small):
    relaxed = build(small, None, integer=False, form="indicator")
    with pytest.raises(Exception) as error:
        quiet_solve(relaxed.model, mathopt.SolverType.GLOP)
    assert "does not support indicator constraints" in str(error.value.__context__)


def test_job_shop_makespan_11_three_ways_and_the_hull_bound_is_tighter():
    from job_shop import cpsat_makespan, mathopt_job_shop
    assert cpsat_makespan() == 11
    bounds = {}
    for form in ("big_m", "hull"):
        assert quiet_solve(mathopt_job_shop(form), mathopt.SolverType.HIGHS).objective_value() == pytest.approx(11)
        bounds[form] = quiet_solve(mathopt_job_shop(form, integer=False), mathopt.SolverType.GLOP).objective_value()
    assert bounds["big_m"] == pytest.approx(7) and bounds["hull"] == pytest.approx(8.2)
