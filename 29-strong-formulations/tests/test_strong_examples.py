"""The module 29 examples: front forms, derived rows, symmetry and the case study's checks."""

import itertools

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_split import assignment, build as build_split, build_counts, params, region_jobs, solve
from derived_rows import already_a_row, cliques, conflicts, fixable
from strong_model import EXACT, build, gap_closed, lp_bound, solve_highs


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def tiny():
    return generate("tiny")


@pytest.fixture(scope="module")
def ridge():
    return region_jobs(generate("medium"), "Ridge")


def test_both_front_forms_give_the_same_optimum_and_the_disaggregated_lp_is_lower(small):
    lp = {f: lp_bound(build(small, integer=False, fronts=f).model).objective_value()
          for f in ("aggregated", "disaggregated")}
    milp = {f: solve_highs(build(small, fronts=f).model, EXACT).objective_value()
            for f in ("aggregated", "disaggregated")}
    assert milp["aggregated"] == pytest.approx(milp["disaggregated"]) == pytest.approx(17_748)
    assert lp["disaggregated"] < lp["aggregated"]
    assert gap_closed(lp["aggregated"], lp["disaggregated"], milp["aggregated"]) == pytest.approx(0.548, abs=1e-3)


def test_a_whole_plan_satisfies_the_aggregated_row_exactly_when_it_satisfies_the_disaggregated_rows():
    # One front of three projects: check all 16 points (y, x1, x2, x3) in {0, 1}^4.
    for y, *xs in itertools.product((0, 1), repeat=4):
        assert (sum(xs) <= 3 * y) == all(x <= y for x in xs)


def test_fixed_starts_are_never_used_by_an_optimal_plan_and_keep_the_optimum(small):
    fixed = fixable(small)
    assert len(fixed) == 8
    plain = solve_highs(build(small, fronts=None, crews=True).model, EXACT)
    sm = build(small, fronts=None, crews=True)
    for start in fixed:
        sm.x[start].upper_bound = 0
    assert solve_highs(sm.model, EXACT).objective_value() == pytest.approx(plain.objective_value())


def test_every_derived_row_holds_for_every_allowed_plan_of_tiny(tiny):
    sm = build(tiny, fronts=None, crews=True)
    starts = list(sm.x)
    rows = [(c.lower_bound, {t.variable: t.coefficient for t in c.terms()}, c.upper_bound)
            for c in sm.model.linear_constraints()]
    fixed = fixable(tiny)
    groups = cliques(conflicts(tiny, fixed))
    plans = 0
    for values in itertools.product((0, 1), repeat=len(starts)):
        point = {sm.x[s]: v for s, v in zip(starts, values)}
        if all(lo - 1e-9 <= sum(a * point[v] for v, a in terms.items()) <= hi + 1e-9 for lo, terms, hi in rows):
            plans += 1
            plan = dict(zip(starts, values))
            assert not any(plan[s] for s in fixed)
            assert all(sum(plan[s] for s in g) <= 1 for g in groups)
    assert plans == 15


def test_clique_rows_keep_the_optimum_and_lower_the_lp_bound(small):
    fixed = fixable(small)
    groups = [c for c in cliques(conflicts(small, fixed)) if not already_a_row(c, small)]

    def model(integer, with_cliques):
        sm = build(small, integer=integer, fronts=None, crews=True)
        for start in fixed:
            sm.x[start].upper_bound = 0
        if with_cliques:
            for group in groups:
                sm.model.add_linear_constraint(sum(sm.x[s] for s in group) <= 1)
        return sm.model

    assert lp_bound(model(False, True)).objective_value() < lp_bound(model(False, False)).objective_value()
    assert solve_highs(model(True, True), EXACT).objective_value() == pytest.approx(22_741)


def test_every_crew_numbering_and_every_order_row_give_the_same_makespan(ridge):
    spans = {round(solve(build_split(ridge, 4, order), detect).objective_value())
             for order in (None, "load", "index") for detect in (False, True)}
    assert spans == {43}
    assert round(solve(build_counts(ridge, 4)).objective_value()) == 43


def test_node_counts_repeat_and_the_order_rows_cut_the_plain_search(ridge):
    counts = [solve(build_split(ridge, 4), False).solve_stats.node_count for _ in range(2)]
    assert counts[0] == counts[1] == 3913
    assert solve(build_split(ridge, 4, "index"), False).solve_stats.node_count < counts[0]


def test_the_index_order_refuses_a_renumbered_plan_and_keeps_one_copy(ridge):
    cs = build_split(ridge, 4)
    plan = assignment(cs, solve(cs))
    ordered = build_split(ridge, 4, "index")

    def allowed(crews_jobs):
        model = ordered.model
        for (j, k), v in ordered.x.items():
            v.lower_bound = v.upper_bound = 1.0 if j in crews_jobs[k] else 0.0
        return solve_highs(model, params(True)).termination.reason == mathopt.TerminationReason.OPTIMAL

    by_first = sorted(plan, key=lambda crew: list(ridge).index(crew[0]))       # renumber by first job
    assert allowed(by_first)
    assert not allowed(list(reversed(by_first)))
