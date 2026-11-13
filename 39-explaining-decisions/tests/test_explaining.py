"""The module 39 examples: binding rows, forced re-solves, scenario diffs and the run record."""

import pytest

from gridcap import generate

from binding import refusals, slack_table
from diffs import diff_scenarios, input_changes
from explain_model import TOL, Scenario, build, slack, solve, solve_highs
from record import make_record, verify
from why import force, rule_facts


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def base(small):
    return solve(build(small))


def test_the_base_plan_is_the_one_module_26_solved(base):
    assert base.status == "OPTIMAL"
    assert base.npv == pytest.approx(24260)
    assert len(base.plan) == 27


def test_no_budget_row_binds_but_every_must_row_does(base):
    table = slack_table(base.built, base.plan)
    budget = {name: s for name, fam, s in table if fam == "budget"}
    assert budget == pytest.approx({"budget_2027": 140, "budget_2028": 150, "budget_2029": 130,
                                    "budget_2030": 50, "budget_2031": 130})
    assert all(abs(s) <= TOL for name, fam, s in table if fam == "must")


def test_slack_reads_both_sides_of_an_equality(small, base):
    values = {v: 0.0 for v in base.built.x.values()}
    assert slack(base.built.rows["must_P003"], values) == pytest.approx(-1)


def test_no_single_addition_fits_and_budgets_refuse_most(base):
    refused = refusals(base.built, base.plan)
    assert len(refused) == 25
    assert all(refused.values())
    assert sum("budget_2030" in rows for rows in refused.values()) == 15


def test_the_lp_relaxation_has_a_binding_row_priced_at_zero(small):
    relaxed = build(small, integer=False)
    result = solve_highs(relaxed.model)
    values = result.variable_values()
    row = relaxed.rows["must_P003"]
    assert abs(slack(row, values)) <= TOL
    assert abs(result.dual_values(row)) <= TOL


def test_the_milp_has_no_dual_values(base):
    with pytest.raises(ValueError):
        base.result.dual_values(base.built.rows["budget_2030"])


def test_forcing_prices_decisions(small, base):
    p024 = force(small, Scenario(), base, "P024")
    assert (p024.action, p024.cost) == ("in", 273)
    p032 = force(small, Scenario(), base, "P032")
    assert (p032.action, p032.cost) == ("out", 112)
    must = force(small, Scenario(), base, "P017")
    assert (must.status, must.cost) == ("INFEASIBLE", None)


def test_a_deferred_alternative_names_the_option_taken(small, base):
    facts = rule_facts(small, base, "P002")
    assert facts[0] == {"row": "alt_G001", "funded": ["P001"]}


def test_the_budget_cut_diff(small, base):
    cut = solve(build(small, Scenario("cut", budget={2029: 6000})))
    d = diff_scenarios(base, cut)
    assert d.selected == ["P002", "P037"]
    assert d.deferred == ["P001", "P005", "P016"]
    assert len(d.shifted) == 6
    assert d.npv == pytest.approx(-1174)
    assert d.spend[2029] == -2940


def test_input_changes_name_every_changed_leaf():
    assert input_changes({"a": 1, "b": {"x": 2}}, {"a": 1, "b": {"x": 3}, "c": 4}) == \
        ["b.x: 2 -> 3", "c: absent -> 4"]


def test_the_record_checks_pass_and_verify_catches_a_broken_plan(small):
    record = make_record(small, Scenario("base"), Scenario("cut-2029", budget={2029: 6000}))
    assert all(ok for _, ok in record["checks"])
    assert record["rerun_same_plan"] is True
    broken = dict(record["plan"])
    broken["P001"] = 2028                   # its alternative P002 is funded too
    failed = [rule for rule, ok in verify(small, Scenario(budget={2029: 6000}), broken) if not ok]
    assert "at most one option per alternative group" in failed
