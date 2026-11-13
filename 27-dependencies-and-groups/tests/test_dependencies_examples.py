"""The module 27 examples: mandates, bundles, alternatives, lags, spend limits and overrides."""

from dataclasses import replace

import pytest

from gridcap import generate
from override_tools import Override, apply, undo
from planning_model import add_after, build, groups_of, schedule, solve_highs, status


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(plan):
    result = solve_highs(plan.model)
    assert status(result) == "OPTIMAL"
    return result


def test_the_base_plan_keeps_every_rule(small):
    plan = build(small)
    result = solve(plan)
    starts = schedule(plan, result)
    assert result.objective_value() == pytest.approx(24_260)
    assert all(p.project_id in starts for p in small.projects if p.must_do)
    for members in groups_of(small).values():
        assert sum(i in starts for i in members) <= 1
    for c in small.projects:
        if c.parent and c.project_id in starts:
            assert starts[c.project_id] >= starts[c.parent] + c.parent_lag
    spend = {y: 0 for y in small.years}
    for i, t in starts.items():
        for y, amount in small.project(i).spend(t).items():
            spend[y] += amount
    assert all(spend[y] <= small.budget[y] for y in small.years)


def test_a_must_do_that_cannot_fit_is_infeasible_and_a_weight_hides_it(small):
    import must_do_rows
    cut = replace(small, budget={**small.budget, 2030: 4_000, 2031: 4_000})
    assert status(solve_highs(must_do_rows.equality(cut)[0].model)) == "INFEASIBLE"
    plan, _ = must_do_rows.weighted(cut)
    assert "P017" not in schedule(plan, solve(plan))


def test_the_must_do_precheck_is_necessary_not_sufficient(small):
    import must_do_load
    assert must_do_load.precheck(replace(small, budget={**small.budget, 2030: 4_000, 2031: 4_000}))
    tight = replace(small, budget={**small.budget, 2030: 5_000, 2031: 5_400})
    assert must_do_load.precheck(tight) == []
    assert status(solve_highs(build(tight).model)) == "INFEASIBLE"


def test_mandate_costs_do_not_add_up():
    import cost_of_mandates as c
    with_all, _ = c.best(set())
    singles = sum(c.best({i})[0] - with_all for i in c.must)
    joint = c.best(set(c.must))[0] - with_all
    assert singles == pytest.approx(2_367)
    assert joint == pytest.approx(2_386)


def test_needs_all_costs_more_than_needs_any(small):
    import needs_rows
    values = {}
    for rule in (needs_rows.needs_all, needs_rows.needs_any):
        plan = build(small)
        rule(plan)
        values[rule.__name__] = solve(plan).objective_value()
    assert values["needs_any"] - values["needs_all"] == pytest.approx(597)


def test_a_same_year_bundle_starts_together_or_not_at_all(small):
    import bundles
    members = bundles.BUNDLES["Ridge vegetation"]
    plan = build(small)
    bundles.same_year(plan, members)
    starts = schedule(plan, solve(plan))
    assert len({starts.get(i) for i in members}) == 1


def test_the_dependency_check_finds_what_the_solver_does_not(small):
    import dependency_check as d
    assert d.check(small) == []
    late = d.edit(small, "P016", parent_lag=2)
    assert any("can never start" in m for m in d.check(late))
    plan = build(late)
    assert "P016" not in schedule(plan, solve(plan))


def test_the_alternative_row_stops_a_double_count(small):
    plan = build(small, alternatives=False)
    starts = schedule(plan, solve(plan))
    assert {"P001", "P002"} <= set(starts)


def test_the_gap_rows_accept_exactly_the_spaced_sequences():
    import repair_then_replace as r
    accepted = {pair for pair in [(2027, 2029), (2027, 2030), (2028, 2030), (2027, 2028), (2028, 2029), (2028, 2028)]
                if r.allows(r.gap_rows, *pair) == "allowed"}
    assert accepted == {(2027, 2029), (2027, 2030), (2028, 2030)}


def test_finish_to_start_rules_out_p023(small):
    import lag_types
    plan = build(small, parents=False)
    for c in small.projects:
        if c.parent:
            add_after(plan, small.project(c.parent), c, lag_types.finish_to_start(small.project(c.parent), c))
    assert "P023" not in schedule(plan, solve(plan))


def test_a_full_spend_floor_costs_more_than_a_fifth_of_the_value(small):
    plan = build(small)
    for y in small.years:
        plan.model.add_linear_constraint(plan.spend[y] >= small.budget[y])
    assert solve(plan).objective_value() < 0.8 * 24_260


def test_tripled_region_floors_pass_the_precheck_and_are_infeasible(small):
    import region_floors as rf
    tripled = {r: 3 * v for r, v in small.region_floor.items()}
    assert rf.precheck(small, tripled) == []
    plan = build(small)
    rf.add_floors(plan, tripled)
    assert status(solve_highs(plan.model)) == "INFEASIBLE"


def test_overrides_add_one_row_and_undo_restores_the_plan(small):
    plan = build(small)
    rows = plan.model.get_num_linear_constraints()
    overrides = [Override("P036", "year", 2028), Override("P032", "out"),
                 Override("P021", "not_before", 2030), Override("P024", "in")]
    changes = [apply(plan, o) for o in overrides]
    assert plan.model.get_num_linear_constraints() == rows + 1
    starts = schedule(plan, solve(plan))
    assert starts.get("P036") == 2028 and "P032" not in starts and "P024" in starts
    for c in reversed(changes):
        undo(plan, c)
    assert plan.model.get_num_linear_constraints() == rows
    assert solve(plan).objective_value() == pytest.approx(24_260)


def test_an_override_outside_the_window_drops_the_project(small):
    plan = build(small)
    apply(plan, Override("P038", "year", 2029))
    assert "P038" not in schedule(plan, solve(plan))
