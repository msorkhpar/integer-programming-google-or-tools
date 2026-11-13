from itertools import combinations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from water_properties import must_dos_funded, prerequisites_funded, within_both_budgets

CI = settings(max_examples=80, derandomize=True, database=None, deadline=None, report_multiple_bugs=False)


@st.composite
def instances(draw):
    """Up to six projects, feasible by construction: budgets fit a drawn valid plan."""
    names = [f"w{k}" for k in range(1, draw(st.integers(1, 6)) + 1)]
    cost, needs, value, witness = {}, {}, {}, set()
    for k, name in enumerate(names):
        cost[name] = (draw(st.integers(1, 40)), draw(st.integers(1, 10)))
        value[name] = draw(st.integers(1, 20))
        needs[name] = draw(st.lists(st.sampled_from(names[:k]), unique=True, max_size=2)) if k else []
        if all(q in witness for q in needs[name]) and draw(st.booleans()):
            witness.add(name)
    must = [p for p in names if p in witness and draw(st.booleans())]
    capital = sum(cost[p][0] for p in witness) + draw(st.integers(0, 30))
    operating = sum(cost[p][1] for p in witness) + draw(st.integers(0, 8))
    return {"cost": cost, "budget": (capital, operating), "must": must, "needs": needs, "value": value}


def solver(capital=True, operating=True, must=True, needs="all"):
    """The best plan by brute force, under the rules switched on; ties go to the first plan found."""
    def solve(instance):
        names = sorted(instance["cost"])
        best, best_value = set(), -1
        for r in range(len(names) + 1):
            for chosen in combinations(names, r):
                plan = set(chosen)
                if capital and sum(instance["cost"][p][0] for p in plan) > instance["budget"][0]:
                    continue
                if operating and sum(instance["cost"][p][1] for p in plan) > instance["budget"][1]:
                    continue
                if must and not all(p in plan for p in instance["must"]):
                    continue
                if needs == "all" and not all(q in plan for p in plan for q in instance["needs"][p]):
                    continue
                if needs == "any" and not all(not instance["needs"][p] or any(q in plan for q in instance["needs"][p])
                                              for p in plan):
                    continue
                v = sum(instance["value"][p] for p in plan)
                if v > best_value:
                    best, best_value = plan, v
        return best
    return solve


# A project with two prerequisites, and money for only one of them besides itself.
TWO_NEEDS = {"cost": {"w1": (10, 1), "w2": (10, 1), "w3": (10, 1)}, "budget": (20, 3), "must": [],
             "needs": {"w1": [], "w2": [], "w3": ["w1", "w2"]}, "value": {"w1": 1, "w2": 1, "w3": 20}}


def holds(prop, solve):
    """True if `prop` holds on the plan `solve` returns for every drawn instance (and TWO_NEEDS)."""
    @CI
    @example(TWO_NEEDS)
    @given(instances())
    def run(instance):
        prop(instance, solve(instance))
    try:
        run()
    except AssertionError:
        return False
    return True


CORRECT = solver()


def test_the_budget_property_holds_and_catches_a_solver_with_no_budgets():
    assert holds(within_both_budgets, CORRECT)
    assert not holds(within_both_budgets, solver(capital=False, operating=False))


def test_the_must_do_property_holds_and_catches_a_solver_that_skips_them():
    assert holds(must_dos_funded, CORRECT)
    assert not holds(must_dos_funded, solver(must=False))


def test_the_prerequisite_property_holds_and_catches_a_solver_without_them():
    assert holds(prerequisites_funded, CORRECT)
    assert not holds(prerequisites_funded, solver(needs="none"))


def test_the_budget_property_checks_the_operating_fund_too():
    assert holds(within_both_budgets, CORRECT)
    assert not holds(within_both_budgets, solver(operating=False))


def test_the_prerequisite_property_needs_every_prerequisite():
    assert holds(prerequisites_funded, CORRECT)
    assert not holds(prerequisites_funded, solver(needs="any"))
