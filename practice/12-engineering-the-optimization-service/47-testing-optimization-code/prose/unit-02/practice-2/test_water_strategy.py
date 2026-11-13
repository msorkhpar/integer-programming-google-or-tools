from itertools import combinations

from hypothesis import find, given, settings
from hypothesis.errors import NoSuchExample

from water_strategy import instances

CI = settings(max_examples=150, derandomize=True, database=None, deadline=None)


def valid(instance, plan):
    cost, (capital, operating) = instance["cost"], instance["budget"]
    return (sum(cost[p][0] for p in plan) <= capital and sum(cost[p][1] for p in plan) <= operating
            and all(p in plan for p in instance["must"])
            and all(q in plan for p in plan for q in instance["needs"][p]))


def has_cycle(needs):
    state = {}

    def visit(p):
        if state.get(p) == "open":
            return True
        if state.get(p) == "done":
            return False
        state[p] = "open"
        found = any(visit(q) for q in needs[p])
        state[p] = "done"
        return found
    return any(visit(p) for p in needs)


@CI
@given(instances())
def test_every_instance_is_well_formed(instance):
    assert set(instance) == {"cost", "budget", "must", "needs", "value"}
    names = set(instance["cost"])
    assert 1 <= len(names) <= 6
    assert set(instance["needs"]) == names and set(instance["value"]) == names
    assert set(instance["must"]) <= names
    for p, prerequisites in instance["needs"].items():
        assert p not in prerequisites and set(prerequisites) <= names


@CI
@given(instances())
def test_every_instance_has_a_valid_plan(instance):
    assert instance["cost"], "an instance needs projects"
    names = sorted(instance["cost"])
    assert any(valid(instance, set(c)) for r in range(len(names) + 1) for c in combinations(names, r))


@CI
@given(instances())
def test_prerequisites_never_form_a_cycle(instance):
    assert instance["cost"], "an instance needs projects"
    assert not has_cycle(instance["needs"])


def test_some_instance_has_a_budget_that_binds():
    def everything_breaks_a_budget(instance):
        cost, (capital, operating) = instance["cost"], instance["budget"]
        return sum(c[0] for c in cost.values()) > capital or sum(c[1] for c in cost.values()) > operating
    try:
        find(instances(), everything_breaks_a_budget, settings=CI)
    except NoSuchExample:
        assert False, "in every drawn instance the budgets fit every project at once"
