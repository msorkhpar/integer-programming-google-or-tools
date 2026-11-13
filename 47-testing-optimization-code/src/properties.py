"""Properties of the planning model that must hold on every drawn portfolio, and their settings.

Each property is a plain function of one drawn case and a rule set. `property_test` wraps one in
Hypothesis's `@given` with the course's settings, so the same property runs on the real rules
(tests/test_properties.py) and on a broken copy (hypothesis_finds.py).
"""

from __future__ import annotations

from dataclasses import replace

from hypothesis import example, given, note, settings

from audit import spend_by_year, value, violations
from plan_model import RULES, optimize
from strategies import Case, cases
from tiny import portfolio, project

#: Same cases on every run and every machine, no example database, no per-example clock limit.
CI = settings(max_examples=60, derandomize=True, database=None, deadline=None)

TOL = 1e-3   # HiGHS's objective carries noise near 1e-5; money is whole $k


def plan_obeys_every_rule(case: Case, rules: dict = RULES) -> None:
    status, npv, plan = optimize(case.portfolio, rules)
    note(f"plan {plan}")
    assert status == "OPTIMAL"                                   # the witness proves it is feasible
    assert violations(case.portfolio, plan) == []


def spend_within_budget(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    spend = spend_by_year(case.portfolio, plan)
    assert all(spend[y] <= case.portfolio.budget[y] for y in case.portfolio.years)


def must_dos_always_funded(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    assert all(p.project_id in plan for p in case.portfolio.projects if p.must_do)


def children_never_without_parents(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    for p in case.portfolio.projects:
        if p.parent and p.project_id in plan:
            assert p.parent in plan
            assert plan[p.project_id] >= plan[p.parent] + p.parent_lag


def reported_value_is_the_plans_value(case: Case, rules: dict = RULES) -> None:
    _, npv, plan = optimize(case.portfolio, rules)
    assert abs(npv - value(case.portfolio, plan)) <= TOL


def never_worse_than_the_witness(case: Case, rules: dict = RULES) -> None:
    _, npv, _ = optimize(case.portfolio, rules)
    assert npv >= value(case.portfolio, case.witness) - TOL


def more_budget_never_lowers_the_value(case: Case, rules: dict = RULES) -> None:
    _, before, _ = optimize(case.portfolio, rules)
    richer = replace(case.portfolio, budget={y: b + 25 for y, b in case.portfolio.budget.items()})
    _, after, _ = optimize(richer, rules)
    assert after >= before - TOL


PROPERTIES = [plan_obeys_every_rule, spend_within_budget, must_dos_always_funded,
              children_never_without_parents, reported_value_is_the_plans_value,
              never_worse_than_the_witness, more_budget_never_lowers_the_value]


#: Cases Hypothesis once shrank a failure to, kept so every run tries them first (lesson 12.3.2).
PINNED = [
    Case(portfolio(project("P1", (1,), (2027, 2028), npv=0),
                   project("P2", (1,), (2027, 2028), npv=1, parent="P1", lag=1),
                   budget={2027: 0, 2028: 2, 2029: 0}), witness={}),
]


def property_test(check, rules: dict = RULES, config: settings = CI, pinned: bool = True):
    """`check` as a Hypothesis test over drawn cases, on the given rules, pinned cases first."""
    @config
    @given(cases())
    def run(case: Case) -> None:
        check(case, rules)
    for case in PINNED if pinned else []:
        run = example(case)(run)
    run.__name__ = run.__qualname__ = check.__name__
    return run
