"""The module 10 examples compute what their lessons say they print."""

from fractions import Fraction

import pytest
from ortools.math_opt.python import mathopt

from covers import cover_rounds, is_cover, is_minimal, lp_with_cuts, separate, violation
from gridcap import generate
from heuristics import (Relaxation, broken, dive, greedy_fill, rins, rins_fixings, round_down, round_nearest,
                        rows_of, value)
from mip_log import SOURCES, progress, relative_gap
from presolve import BinaryModel, Row, activity, from_selection, presolve, tighten, to_mathopt
from selection import five_year, knapsack, mask_times, solve_quiet, solve_with_log
from tableau import build, frac, gomory, in_original_variables, solve, value_of

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@pytest.fixture(scope="module")
def tiny():
    return generate("tiny")


@pytest.fixture(scope="module")
def medium():
    return generate("medium")


@pytest.fixture(scope="module")
def medium_lp(medium):
    model = five_year(medium).model
    return model, rows_of(model), Relaxation(five_year(medium).model).solve()


# 3.3.1 Cutting planes


def test_the_tiny_knapsack_lp_overestimates_by_its_integrality_gap(tiny):
    lp = mathopt.solve(knapsack(tiny, integer=False).model, mathopt.SolverType.GLOP)
    milp = solve_quiet(knapsack(tiny).model)
    assert lp.objective_value() == pytest.approx(5005.3, abs=0.05)
    assert milp.objective_value() == pytest.approx(4876)


def test_the_hand_cover_is_minimal_violated_and_found_by_separation(tiny):
    values = {p.project_id: p.value for p in tiny.projects}
    a = {p.project_id: p.capex for p in tiny.projects}
    _, x = lp_with_cuts(values, a, tiny.capital_budget, [])
    cover = ["P001", "P004", "P006", "P007"]
    assert is_cover(cover, a, tiny.capital_budget) and is_minimal(cover, a, tiny.capital_budget)
    assert violation(cover, x) > 0.98
    assert sorted(separate(a, tiny.capital_budget, x)) == sorted(cover)
    assert not is_minimal(cover + ["P005"], a, tiny.capital_budget)


def test_cover_rounds_never_raise_the_bound_and_stay_above_the_optimum(tiny):
    values = {p.project_id: p.value for p in tiny.projects}
    a = {p.project_id: p.capex for p in tiny.projects}
    bounds = [bound for _, bound, _, _ in cover_rounds(values, a, tiny.capital_budget)]
    assert bounds == sorted(bounds, reverse=True)
    assert bounds[-1] >= 4876 - 1e-6 and len(bounds) == 3


def test_one_gomory_cut_solves_the_package_model():
    A, b, c = [[1, 1], [5, 9]], [6, 45], [5, 8]
    T = solve(build(A, b, c, ["d", "t"]))
    assert [value_of(T, 0), value_of(T, 1)] == [Fraction(9, 4), Fraction(15, 4)]
    coef, rhs = gomory(T.rows[T.basis.index(1)])
    assert in_original_variables(coef, rhs, A, b) == ([2, 3], 15)
    T2 = solve(build(A + [[2, 3]], b + [15], c, ["d", "t"]))
    assert [value_of(T2, 0), value_of(T2, 1)] == [0, 5] and T2.rows[-1][-1] == 40


def test_the_fractional_part_uses_the_floor():
    assert frac(Fraction(-5, 4)) == Fraction(3, 4) and frac(Fraction(9, 4)) == Fraction(1, 4)


# 3.3.2 Presolve


def test_our_presolve_shrinks_the_five_year_model_and_keeps_its_optimum(medium):
    full = five_year(medium)
    original = from_selection(full.model)
    done = presolve(original)
    assert (len(original.rows), len(original.objective)) == (80, 400)
    assert (len(done.model.rows), len(done.model.objective)) == (35, 199)
    model, x = to_mathopt(done.model)
    reduced = solve_quiet(model, params=EXACT)
    plan = dict(done.fixed)
    plan.update({j: round(reduced.variable_values(v)) for j, v in x.items()})
    assert reduced.objective_value() + done.constant == pytest.approx(274999)
    assert broken(original, plan) == []
    assert solve_quiet(full.model, params=EXACT).objective_value() == pytest.approx(274999)


def test_activity_fixes_projects_a_must_do_leaves_no_room_for():
    toy = BinaryModel({"PA": 7, "PB": 5, "PC": 4},
                      {"budget": Row({"PA": 6, "PB": 4, "PC": 3}, "<=", 8), "must_PA": Row({"PA": 1}, "==", 1)})
    assert presolve(toy).fixed == {"PA": 1, "PB": 0, "PC": 0}


def test_an_impossible_row_is_reported():
    toy = BinaryModel({"PA": 7, "PB": 5}, {"budget": Row({"PA": 6, "PB": 4}, "<=", 5), "must_PA": Row({"PA": 1}, "==", 1)})
    with pytest.raises(ValueError):
        presolve(toy)


def test_coefficient_tightening_keeps_every_01_plan():
    row = Row({"PA": 5, "PB": 2, "PC": 2}, "<=", 6)
    original = Row(dict(row.coefs), "<=", row.rhs)
    lo, hi = dict.fromkeys(row.coefs, 0), dict.fromkeys(row.coefs, 1)
    assert tighten(row, lo, hi) == [("PA", 5, 3)] and row.rhs == 4
    for bits in range(8):
        plan = {j: (bits >> k) & 1 for k, j in enumerate(sorted(row.coefs))}
        fits = lambda r: sum(a * plan[j] for j, a in r.coefs.items()) <= r.rhs
        assert fits(row) == fits(original)
    assert activity(original, lo, hi) == (0, 9)


def test_highs_presolve_and_its_switch(medium):
    model = five_year(medium).model
    _, on = solve_with_log(model)
    _, off = solve_with_log(model, mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF))
    assert any(line.startswith("Presolve reductions: rows 17(-63); columns 172(-228)") for line in on)
    assert not any(line.startswith("Presolving model") for line in off)


# 3.3.3 Primal heuristics


def test_rounding_down_is_feasible_and_nearest_is_not(medium_lp):
    _, m, (bound, x) = medium_lp
    assert broken(m, round_down(x)) == []
    assert broken(m, round_nearest(x)) == ["budget_2028", "budget_2029"]
    assert value(m, round_down(x)) == pytest.approx(271019)


def test_fill_dive_and_rins_climb_toward_the_optimum(medium, medium_lp):
    model, m, (bound, x) = medium_lp
    spend = {j: sum(r.coefs.get(j, 0) for n, r in m.rows.items() if n.startswith("budget")) for j in m.objective}
    filled = greedy_fill(m, round_down(x), spend)
    plan, steps = dive(Relaxation(five_year(medium).model))
    improved, free = rins(model, plan, x)
    values = [value(m, filled), value(m, plan), value(m, improved)]
    assert values == pytest.approx([274418, 274886, 274922])
    assert all(broken(m, p) == [] for p in (filled, plan, improved))
    assert len(steps) == 123 and free == 12 and len(rins_fixings(plan, x)) == 388
    assert max(values) <= 274999 <= bound


# 3.3.4 Reading the log


def test_the_log_rows_and_the_result_agree(medium):
    result, log = solve_with_log(five_year(medium).model)
    rows = progress(log)
    assert [r.src for r in rows if r.src] == ["z", "p", "J", "R", "L", "L", "L"]
    assert all(r.src in SOURCES for r in rows if r.src)
    assert rows[-1].nodes == result.solve_stats.node_count == 79
    bounds = result.termination.objective_bounds
    assert (bounds.primal_bound, bounds.dual_bound) == (274979, 275006)
    assert relative_gap(bounds.dual_bound, bounds.primal_bound) <= 1e-4 < relative_gap(rows[-1].bound, rows[-1].sol)


def test_mask_times_hides_only_times():
    assert mask_times("17 rows, 172 cols, 271 nonzeros  0.01s") == "17 rows, 172 cols, 271 nonzeros  <t>s"
    assert mask_times("  Timing            1.26") == "  Timing            <t>"
    assert mask_times("  Nodes             79") == "  Nodes             79"
