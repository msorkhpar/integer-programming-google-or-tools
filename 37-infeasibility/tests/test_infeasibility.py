"""The module 37 examples: verdicts, pre-solve checks, filters, elastic repairs, CP-SAT conflicts, messages."""

from dataclasses import replace

import pytest
from ortools.math_opt.python import mathopt

from checks import run_checks
from diagnose import runaway, separate
from elastic import best_repair, elastic, fewest_rules, min_violation
from filters import Oracle, additive_filter, deletion_filter
from gridcap import generate
from lock_model import LOCK, Scenario, build, solve
from message import arithmetic, explain


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_the_base_scenario_has_a_plan_and_the_lock_has_none(small):
    assert solve(build(small).model).termination.reason == mathopt.TerminationReason.OPTIMAL
    assert separate(build(small, LOCK).model) == "infeasible"


def test_a_zero_objective_copy_separates_an_unbounded_model():
    m = mathopt.Model()
    x = m.add_variable(lb=0, is_integer=True, name="x")
    y = m.add_variable(lb=0, name="y")
    m.add_linear_constraint(x - y <= 2)
    m.maximize(x + y)
    assert separate(m) == "unbounded"
    assert "y" in runaway(m)


def test_checks_never_refuse_the_base_data_and_find_the_crew_cut(small):
    assert run_checks(small) == []
    assert [(p.check, p.subject) for p in run_checks(small, LOCK)] == [("crews", "P017")]
    assert run_checks(small, replace(LOCK, crews={})) == []


def test_both_filters_return_irreducible_conflicts(small):
    lm = build(small, LOCK)
    rules = list(lm.rules)
    for found in (deletion_filter(Oracle(lm.model), rules), additive_filter(Oracle(lm.model), rules)):
        oracle = Oracle(lm.model)
        assert oracle.infeasible(found)
        assert all(not oracle.infeasible([n for n in found if n != m]) for m in found)


def test_the_deletion_filter_keeps_what_it_tests_last(small):
    lm = build(small, LOCK)
    rules = list(lm.rules)
    assert sorted(deletion_filter(Oracle(lm.model), rules[::-1])) == [
        "crews_transmission_2030", "crews_transmission_2031", "must_P017"]


def test_the_priced_repair_is_feasible_and_cheapest_at_390(small):
    lm = build(small, LOCK)
    soft = [n for n in lm.rules if n.startswith(("budget_", "crews_", "floor_", "force_", "must_"))]
    prices = {"budget_": 1.0, "floor_": 1.0, "crews_": 50.0, "force_": 1e4, "must_": 1e4}
    el = elastic(lm.model, {n: next(w for p, w in prices.items() if n.startswith(p)) for n in soft})
    least = min_violation(el).objective_value()
    assert least == pytest.approx(390)
    assert best_repair(el, least).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_two_rows_is_the_fewest_that_must_bend(small):
    lm = build(small, LOCK)
    soft = [n for n in lm.rules if n.startswith(("budget_", "crews_", "floor_", "force_", "must_"))]
    el = elastic(lm.model, {n: 1.0 for n in soft})
    big = {n: 1 if n.startswith(("force_", "must_")) else 50_000 for n in soft}
    assert fewest_rules(el, big).objective_value() == pytest.approx(2)


def test_the_message_names_projects_and_numbers_not_rows(small):
    conflict = ["must_P017", "crews_transmission_2030", "crews_transmission_2031"]
    text = "\n".join(explain(conflict, small, LOCK))
    assert "P017 Coast tower set repair" in text and "13 crew-months" in text
    assert "crews_transmission" not in text and "must_P017" not in text
    assert len(arithmetic(conflict, small, LOCK)) == 2
    assert arithmetic(conflict, small, Scenario()) == []
