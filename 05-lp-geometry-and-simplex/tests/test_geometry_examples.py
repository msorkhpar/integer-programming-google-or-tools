"""The module 05 examples compute what their lessons say they print."""

import pytest
from ortools.math_opt.python import mathopt

from simplex import entering, leaving, pivot, solve, tableau
from split_lp import BOUNDS, ROWS, VALUE, build

A = [list(a) for a, _ in ROWS.values()]
B = [rhs for _, rhs in ROWS.values()]
NAMES = ["d", "t", "s_budget", "s_crews", "s_ready_t"]


def test_the_region_has_five_vertices_and_the_best_is_c():
    from level_lines import value
    from vertices import vertices
    corners = vertices()
    assert set(corners) == {(0, 0), (24, 0), (12, 18), (10, 20), (0, 20)}
    assert max(corners, key=value) == (12, 18) and value((12, 18)) == 132


def test_plans_break_the_rows_the_lesson_names():
    from half_planes import broken
    assert broken(10, 10) == [] and broken(20, 10) == ["crews"] and broken(16, 16) == ["budget", "crews"]


def test_the_tie_objective_is_optimal_along_an_edge():
    from level_lines import touches
    assert touches(120, (4, 4)) == "touches the region along C, D"


def test_glop_agrees_with_the_picture():
    model, x = build()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    assert result.objective_value() == pytest.approx(132)
    assert result.variable_values(x["d"]) == pytest.approx(12) and result.variable_values(x["t"]) == pytest.approx(18)


def test_one_pivot_moves_from_the_origin_to_b():
    T = tableau(A, B, VALUE)
    k = entering(T)
    r = leaving(T, k)
    assert (k, r) == (0, 1)
    T = pivot(T, r, k)
    assert T[1][-1] == pytest.approx(24) and T[-1][-1] == pytest.approx(120)
    assert [row[0] for row in T] == pytest.approx([0, 1, 0, 0])


def test_simplex_walks_a_b_c():
    result = solve(A, B, VALUE, NAMES)
    assert result.status == "OPTIMAL" and result.value == pytest.approx(132)
    assert [step[3] for step in result.steps] == [pytest.approx([24, 0]), pytest.approx([12, 18])]


def test_the_commitment_makes_the_lp_infeasible_by_four():
    from infeasible_lp import COMMITTED, total_violation
    from vertices import vertices
    assert vertices({**COMMITTED, **BOUNDS}) == {}
    model, _ = build(COMMITTED)
    assert mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.INFEASIBLE
    assert total_violation(ROWS) == pytest.approx(0) and total_violation(COMMITTED) == pytest.approx(4)


def test_losing_the_budget_rows_makes_the_lp_unbounded_along_d():
    result = solve([[0, 1]], [20], VALUE, ["d", "t", "s"])
    assert result.status == "UNBOUNDED" and result.direction == [1.0, 0.0]
    assert solve([[0, 1]], [20], (-1, 4), ["d", "t", "s"]).value == pytest.approx(80)


def test_the_mix_rule_makes_a_step_of_length_zero_and_the_same_optimum():
    from degenerate_lp import MIX
    rows = list(MIX.values())
    result = solve([list(a) for a, _ in rows], [b for _, b in rows], VALUE, NAMES + ["s_mix"])
    assert result.steps[0][2] == 0 and result.value == pytest.approx(132)
    assert len(result.steps) == 3


def test_the_tableau_simplex_matches_glop_on_the_or_tools_sample_lp():
    import simplex_sample
    result = solve(simplex_sample.A, simplex_sample.b, simplex_sample.c, simplex_sample.NAMES + ["s1", "s2", "s3"])
    status, value, x = simplex_sample.glop()
    assert result.status == "OPTIMAL" and status == "OPTIMAL" and len(result.steps) == 2
    assert result.value == pytest.approx(value) == pytest.approx(2200 / 3)
    assert result.x == [pytest.approx(v, abs=1e-9) for v in x]


def test_phase_one_reaches_zero_stretch_at_a_vertex_when_the_origin_breaks_a_satisfiable_row():
    from two_phase import FLOOR, phase_one
    from vertices import vertices
    stretch, d, t = phase_one(FLOOR)
    assert stretch == 0 and (d, t) in vertices({**FLOOR, **BOUNDS})
