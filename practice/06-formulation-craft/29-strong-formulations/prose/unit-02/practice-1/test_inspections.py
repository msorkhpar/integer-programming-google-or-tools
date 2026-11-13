import itertools

from ortools.math_opt.python import mathopt

from inspections import build, tighten

# A regulator's inspection programme (not GridCap): each district needs inspection hours, one budget.


def plans(cost, budget, hours, need):
    """Every allowed 0/1 plan, by brute force."""
    found = []
    for take in itertools.product((0, 1), repeat=len(cost)):
        chosen = {j for j, t in zip(cost, take) if t}
        if sum(cost[j] for j in chosen) <= budget and all(
                sum(h for j, h in gives.items() if j in chosen) >= need[d] for d, gives in hours.items()):
            found.append(chosen)
    return found


def check(cost, budget, hours, need, ones, zeros):
    allowed = plans(cost, budget, hours, need)
    assert allowed, "the instance itself must have a plan"
    assert tighten(cost, budget, hours, need) == (ones, zeros)
    for plan in allowed:                       # every fixing is true of every allowed plan
        assert ones <= plan and not (zeros & plan)


def test_a_district_only_some_inspections_reach_forces_them():
    cost = {"A": 2, "B": 2, "C": 2, "D": 2}
    hours = {"hills": {"A": 4, "B": 3, "C": 0, "D": 1}}
    # Without A the hills get at most 3 + 1 = 4 < 6, so A must run; without B, 4 + 1 = 5 < 6 too.
    check(cost, 10, hours, {"hills": 6}, ones={"A", "B"}, zeros=set())


def test_what_must_run_leaves_no_room_for_an_expensive_one():
    cost = {"A": 5, "B": 2, "C": 6, "D": 1}
    hours = {"coast": {"A": 5, "B": 1, "C": 2, "D": 1}}
    # A is forced (without it at most 4 < 5); 5 spent of 9 leaves 4, so C (6) is out.
    check(cost, 9, hours, {"coast": 5}, ones={"A"}, zeros={"C"})


def test_an_inspection_ruled_out_can_force_another():
    cost = {"A": 4, "B": 5, "C": 1, "D": 1}
    hours = {"north": {"A": 3, "B": 1}, "south": {"B": 2, "C": 1, "D": 1}}
    # Round 1: north needs A. Round 2: A's 4 of a budget of 8 leave 4, so B (5) is out.
    # Round 3: without B the south can get only C and D, 2 hours, so both must run.
    check(cost, 8, hours, {"north": 3, "south": 2}, ones={"A", "C", "D"}, zeros={"B"})


def test_an_inspection_that_exactly_fills_the_budget_is_not_ruled_out():
    cost = {"A": 3, "B": 4, "C": 2}
    hours = {"plains": {"A": 2, "B": 1, "C": 1}}
    # A is forced (without it 2 < 3 hours); 3 + 4 = 7 is exactly the budget, so B may still run.
    check(cost, 7, hours, {"plains": 3}, ones={"A"}, zeros=set())


def test_the_fixings_lower_the_lp_bound_and_keep_the_optimum():
    cost = {"A": 4, "B": 5, "C": 1, "D": 1}
    hours = {"north": {"A": 3, "B": 1}, "south": {"B": 2, "C": 1, "D": 1}}
    need = {"north": 3, "south": 2}
    value = {"A": 1, "B": 9, "C": 1, "D": 1}
    fix = tighten(cost, 8, hours, need)

    def solve(integer, fixings):
        model, _ = build(cost, 8, hours, need, value, integer=integer, fixings=fixings)
        return mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value()

    assert solve(True, fix) == solve(True, None) == 3
    assert solve(False, fix) < solve(False, None) - 1
