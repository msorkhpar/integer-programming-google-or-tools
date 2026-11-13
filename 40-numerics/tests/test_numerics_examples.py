"""The module 40 examples: tolerances, units, rounding, coefficient ranges, rescaling and log signals."""

import math

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from loan_model import EXACT, HUGE_M, MIXED, NO_PRESOLVE, TIGHT, build, coefficient_ranges, row_violations, solve


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_floats_have_the_spacing_the_lesson_prints():
    assert 0.1 + 0.2 != 0.3
    assert 1e16 + 1 == 1e16
    assert math.ulp(1e10) > 1e-6 > math.ulp(8_890_000.0)


@pytest.mark.parametrize("solver, integer, accepted", [
    (mathopt.SolverType.HIGHS, False, (True, False, False)),
    (mathopt.SolverType.HIGHS, True, (True, True, False)),
    (mathopt.SolverType.GSCIP, True, (True, True, False)),
])
def test_rows_broken_by_less_than_the_tolerance_are_accepted(solver, integer, accepted):
    from tolerance_edge import GAPS, squeezed
    for d, want in zip(GAPS, accepted):
        result, _ = solve(squeezed(d, integer), solver)
        assert result.has_primal_feasible_solution() is want


def test_the_same_overrun_is_refused_in_k_and_allowed_in_billions():
    from units import allowed
    assert allowed(0.5, 1, mathopt.SolverType.HIGHS) == "refused"
    assert allowed(0.5, 1e-6, mathopt.SolverType.HIGHS) == "allowed"
    assert allowed(5, 1e-6, mathopt.SolverType.GSCIP) == "refused"


def test_a_huge_m_without_presolve_takes_free_loans_and_its_rounding_overspends(small):
    best, _ = solve(build(small, TIGHT).model, params=EXACT)
    lm = build(small, HUGE_M)
    result, log = solve(lm.model, params=NO_PRESOLVE)
    values = result.variable_values()
    assert result.objective_value() > best.objective_value() + 1
    leaks = [y for y in small.years if values[lm.loan[y]] > 1 and values[lm.take[y]] < 1e-6]
    assert leaks
    assert any("(int. viol.)" in line and not line.strip().startswith("0 ") for line in log)


def test_the_tight_model_ranges_match_highs_log(small):
    lm = build(small, TIGHT)
    _, log = solve(lm.model)
    ranges = coefficient_ranges(lm.model)
    for kind, (low, high) in ranges.items():
        line = next(line for line in log if line.strip().startswith(kind))
        assert f"[{low:.0e}, {high:.0e}]" in line


def test_rescaling_keeps_the_plan_and_shrinks_the_matrix_range(small):
    plans, spans = [], []
    for units in (MIXED, TIGHT):
        lm = build(small, units)
        result, _ = solve(lm.model)
        values = result.variable_values()
        plans.append({i for i, v in lm.x.items() if values[v] > 0.5})
        low, high = coefficient_ranges(lm.model)["Matrix"]
        spans.append(high / low)
        assert lm.in_k(result.objective_value()) == pytest.approx(23_161.5)
    assert plans[0] == plans[1]
    assert spans[1] < 1e4 < 1e9 < spans[0]


def test_highs_drops_a_coefficient_of_1e_9():
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=1000)
    y = model.add_binary_variable()
    model.add_linear_constraint(1e-9 * x + y <= 1, name="row")
    model.maximize(x + y)
    result, log = solve(model)
    assert "1 nonzero;" in log[0]
    assert row_violations(model, result.variable_values())["row"] == pytest.approx(1e-6)


def test_scip_flags_its_solution_and_the_badly_scaled_variants_disagree(small):
    _, log = solve(build(small, HUGE_M).model, mathopt.SolverType.GSCIP, EXACT)
    assert "best solution is not feasible in original problem" in log
    for units in (HUGE_M, MIXED):
        answers = set()
        for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP):
            for params in (EXACT, NO_PRESOLVE):
                lm = build(small, units)
                result, _ = solve(lm.model, solver, params)
                answers.add(round(lm.in_k(result.objective_value()), 1))
        assert len(answers) > 1
