import itertools

from ortools.math_opt.python import mathopt

from depots import Depots, add_inherited_rules, add_rules, build

# A transmission operator's spare-parts depots (not GridCap): five substations, four candidate depots.
DEMAND = {"S1": 4, "S2": 3, "S3": 5, "S4": 2, "S5": 6}
CAPACITY = {"D1": 10, "D2": 12, "D3": 9, "D4": 20}
FEE = {"D1": 30, "D2": 34, "D3": 25, "D4": 60}
HAUL = dict(zip(itertools.product(DEMAND, CAPACITY),
                [2, 5, 7, 9, 3, 2, 6, 8, 6, 4, 2, 7, 8, 6, 3, 5, 5, 7, 4, 2]))
D = Depots(DEMAND, CAPACITY, FEE, HAUL)


def allowed(served_by: dict, open_depots: set) -> bool:
    model, x, y = build(D, add_rules)
    for (i, j), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if served_by[i] == j else 0.0
    for j, var in y.items():
        var.lower_bound = var.upper_bound = 1.0 if j in open_depots else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def bound(rules) -> float:
    model, _, _ = build(D, rules, integer=False)
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_the_same_plans_are_allowed_and_the_best_costs_the_same():
    plan = {"S1": "D1", "S2": "D2", "S3": "D2", "S4": "D3", "S5": "D3"}
    assert allowed(plan, {"D1", "D2", "D3"}) is True
    assert allowed(plan, {"D1", "D2"}) is False                               # S4 and S5 at a closed depot
    assert allowed({**plan, "S1": "D3"}, {"D1", "D2", "D3"}) is False         # D3 would hold 4 + 2 + 6 = 12 > 9
    best = [mathopt.solve(build(D, rules)[0], mathopt.SolverType.HIGHS).objective_value()
            for rules in (add_inherited_rules, add_rules)]
    assert best[0] == best[1] == 77


def test_each_substation_is_tied_to_its_own_depot_switch():
    # The tightest rows found give an LP bound of 72.625 (minimizing: a higher floor is tighter).
    assert bound(add_rules) >= 72.625 - 1e-6


def test_an_open_depot_is_needed_for_any_capacity():
    # Without capacity tied to the depot's switch, the LP opens slivers of depots: a floor near 51.
    assert bound(add_rules) >= 60
