"""One unit test per rule of plan_model: a hand-made instance, an allowed plan and a refused plan.

Each test builds the model with the rule under test alone (`only`), on an instance where that rule
is the only thing that could refuse a plan, and pairs a plan the rule must accept with one it must
refuse, at the boundary where the two meet. Each takes the rule set as an argument, so the same
test runs on the real rules (tests/test_rules.py) and on the broken copies of bugs.py (one_rule.py).
"""

from __future__ import annotations

from plan_model import RULES, accepts, allowed, build
from tiny import portfolio, project


def only(rules: dict, name: str) -> dict:
    """The rule set with every rule but `name` taken out."""
    return {name: rules[name]}


def test_budget_caps_every_year(rules: dict = RULES):
    # A spends 60 in 2028 and 40 in 2029; B spends 1 in 2029. Only 2029's budget is tight.
    data = portfolio(project("A", cost=(60, 40), window=(2028, 2028)),
                     project("B", cost=(1,), window=(2029, 2029)),
                     budget={2029: 40})
    model = build(data, only(rules, "budget"))
    assert allowed(model, {"A": 2028})                   # 40 in 2029: exactly the budget
    assert not allowed(model, {"A": 2028, "B": 2029})    # 41 in 2029: one over


def test_must_do_is_always_funded(rules: dict = RULES):
    data = portfolio(project("M", window=(2027, 2028), must=True))
    model = build(data, only(rules, "must"))
    assert allowed(model, {"M": 2028})                   # its last allowed year
    assert not allowed(model, {})                        # left out


def test_a_project_starts_at_most_once(rules: dict = RULES):
    data = portfolio(project("A", window=(2027, 2028)))
    model = build(data, only(rules, "once"))
    assert accepts(model, {("A", 2027)})
    assert not accepts(model, {("A", 2027), ("A", 2028)})


def test_at_most_one_alternative(rules: dict = RULES):
    data = portfolio(project("R", window=(2027, 2027), alt="G"),
                     project("S", window=(2027, 2028), alt="G"))
    model = build(data, only(rules, "alt"))
    assert allowed(model, {"S": 2028})
    assert not allowed(model, {"R": 2027, "S": 2028})    # both, in different years


def test_child_waits_for_its_parent_and_lag(rules: dict = RULES):
    data = portfolio(project("P", window=(2027, 2028)),
                     project("C", window=(2028, 2029), parent="P", lag=1))
    model = build(data, only(rules, "after"))
    assert allowed(model, {"P": 2027, "C": 2028})        # exactly the lag
    assert not allowed(model, {"P": 2028, "C": 2028})    # one year early
    assert not allowed(model, {"C": 2029})               # no parent at all


TESTS = [test_budget_caps_every_year, test_must_do_is_always_funded, test_a_project_starts_at_most_once,
         test_at_most_one_alternative, test_child_waits_for_its_parent_and_lag]
