"""The module 42 examples: every builder makes the same model, the measuring tools, and the generator's invariants.

No test here measures speed: wall-clock times change between runs and machines, so a speed
assertion would fail at random. The tests check what the timings are about instead: that the
fast builders make exactly the model of the slow one.
"""

from dataclasses import replace

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from growth import exponent, first_projects, first_rows, rows_scanned
from invariants import violations, witness_fits
from loop_builder import build_loops, solve_highs
from matrix_builder import build_matrix, columns, entries
from same_model import canonical, differences
from slow_builder import build_slow
from stopwatch import Timing, measure
from streams import changed, shared_stream, stream_per_project
from tables import tables_of


@pytest.fixture(scope="module")
def large():
    return generate("large")


@pytest.fixture(scope="module")
def large_tables(large):
    return tables_of(large)


@pytest.mark.parametrize("size", ["tiny", "small", "medium"])
def test_the_slow_and_the_matrix_builder_export_the_loop_builders_model(size):
    portfolio = generate(size)
    tables = tables_of(portfolio)
    reference = build_loops(portfolio).export_model()
    assert build_slow(tables).export_model() == reference
    assert build_matrix(tables).export_model() == reference


def test_the_matrix_builder_exports_the_loop_builders_model_on_large(large, large_tables):
    assert build_matrix(large_tables).export_model() == build_loops(large).export_model()


@pytest.mark.parametrize("seed", [5, 2030])
def test_the_builders_agree_at_other_seeds(seed):
    portfolio = generate("medium", seed)
    assert build_matrix(tables_of(portfolio)).export_model() == build_loops(portfolio).export_model()


def test_the_matrix_model_solves_to_the_spread_npv_of_lesson_6_4_2():
    tables = tables_of(generate("small"))
    result = solve_highs(build_matrix(tables))
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert result.objective_value() == pytest.approx(24_260)


def test_the_tables_hold_every_cost_and_every_start():
    small = generate("small")
    t = tables_of(small)
    assert len(t.starts) == sum(len(p.starts()) for p in small.projects)
    capex = t.costs.groupby("project_id")["amount"].sum().to_dict()
    assert capex == {p.project_id: p.capex for p in small.projects}
    assert dict(zip(t.budget["year"], t.budget["budget"])) == dict(small.budget)


def test_names_find_no_difference_where_only_the_order_changed_and_find_a_late_cost():
    small = generate("small")
    tables = tables_of(small)
    loops = build_loops(small)
    year_first = build_matrix(replace(tables, starts=tables.starts.sort_values(["start", "project_id"])))
    assert loops.export_model() != year_first.export_model()
    assert differences(loops, year_first) == []
    assert canonical(loops) == canonical(year_first)
    late = build_matrix(replace(tables, costs=tables.costs.assign(k=tables.costs["k"] + 1)))
    assert differences(loops, late)[0].startswith("row budget_2027")


def test_measure_warms_up_then_times_each_repeat_on_its_own_clock():
    ticks = iter([0.0, 1.0, 10.0, 13.0, 20.0, 22.0])
    calls = []
    timing = measure(lambda: calls.append(1), repeats=3, warmup=2, clock=lambda: next(ticks))
    assert len(calls) == 5
    assert timing.samples == (1.0, 3.0, 2.0)
    assert (timing.median, timing.low, timing.high) == (2.0, 1.0, 3.0)
    assert Timing((4.0, 1.0, 3.0, 2.0)).median == 2.5


def test_the_fitted_exponent_is_two_for_quadratic_and_one_for_linear_times():
    sizes = (1_000, 2_000, 4_000)
    assert exponent(sizes, [n ** 2 * 1e-6 for n in sizes]) == pytest.approx(2.0)
    assert exponent(sizes, [n * 3e-5 for n in sizes]) == pytest.approx(1.0)


def test_a_prefix_of_large_keeps_every_parent_and_the_scan_count_grows_about_fourfold(large, large_tables):
    prefix = first_projects(large, 2_500)
    ids = {p.project_id for p in prefix.projects}
    assert all(p.parent in ids for p in prefix.projects if p.parent)
    counts = [rows_scanned(first_rows(large_tables, n)) for n in (2_500, 5_000)]
    assert 3.5 < counts[1] / counts[0] < 4.5


def test_large_has_the_sizes_the_lessons_quote(large_tables):
    cols = columns(large_tables)
    rows, terms = entries(cols, large_tables)
    assert (len(cols), len(rows), len(terms)) == (21_843, 11_467, 63_048)


@pytest.mark.parametrize("seed", [2027, 2040, 7])
def test_large_keeps_every_invariant_and_its_must_do_plan_is_feasible(seed):
    portfolio = generate("large", seed)
    assert violations(portfolio) == []
    assert witness_fits(portfolio)


@pytest.mark.parametrize("size", ["tiny", "small", "medium"])
def test_every_size_keeps_every_invariant(size):
    assert violations(generate(size)) == []


def test_a_planted_overspend_breaks_the_budget_rules_and_the_must_do_plan(large):
    must = next(q for q in large.projects if q.must_do)
    heavier = replace(must, cost_profile=(must.cost_profile[0] + large.budget[must.earliest_start],)
                      + must.cost_profile[1:])
    planted = replace(large, projects=tuple(heavier if q is must else q for q in large.projects))
    found = violations(planted)
    assert any(v.startswith("must-dos fit the yearly budget") for v in found)
    assert not witness_fits(planted)


def test_a_new_draw_shifts_a_shared_stream_but_not_streams_per_project():
    assert changed(shared_stream(8, 7), shared_stream(8, 7, version=2)) == [5, 6, 7, 8]
    assert changed(stream_per_project(8, 7), stream_per_project(8, 7, version=2)) == []
    assert stream_per_project(100, 7)[:8] == stream_per_project(8, 7)
