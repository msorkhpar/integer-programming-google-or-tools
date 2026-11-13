from ortools.math_opt.python import mathopt

from advance import add_advances

# Each project's spend by year, $k: a water main, a pump station, a meter roll-out, valves and a tank.
WORK = {
    "main": {2027: 300},
    "pumps": {2027: 100, 2028: 150},
    "meters": {2028: 200},
    "valves": {2028: 60},
    "tank": {2029: 120},
}


def allowed(plan: set[str], budgets: dict[int, int], share: float) -> bool:
    model = mathopt.Model()
    x = {name: model.add_binary_variable(name=name) for name in WORK}
    spend = {y: sum(cost.get(y, 0) * x[name] for name, cost in WORK.items()) for y in budgets}
    add_advances(model, spend, budgets, share)
    for name, var in x.items():
        value = 1.0 if name in plan else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_plan_within_every_year_is_allowed_and_an_overspend_beyond_the_advance_refused():
    plan = {"main", "pumps", "meters", "tank"}
    assert allowed(plan, {2027: 400, 2028: 350, 2029: 120}, 0.1) is True
    assert allowed(plan, {2027: 300, 2028: 350, 2029: 120}, 0.1) is False


def test_the_advance_is_capped_by_the_budget_it_is_taken_from():
    assert allowed({"main", "pumps"}, {2027: 360, 2028: 400, 2029: 200}, 0.1) is True
    assert allowed({"main", "pumps"}, {2027: 360, 2028: 400, 2029: 200}, 0.05) is False


def test_an_advance_is_taken_off_the_next_years_money():
    plan = {"main", "pumps", "meters", "valves"}
    assert allowed(plan, {2027: 400, 2028: 420, 2029: 200}, 0.1) is True
    assert allowed(plan, {2027: 360, 2028: 420, 2029: 200}, 0.1) is False


def test_the_last_year_cannot_borrow():
    assert allowed({"tank"}, {2027: 400, 2028: 400, 2029: 120}, 0.5) is True
    assert allowed({"tank"}, {2027: 400, 2028: 400, 2029: 100}, 0.5) is False


def test_money_left_unspent_lapses():
    assert allowed({"pumps"}, {2027: 400, 2028: 300, 2029: 400}, 0.1) is True
    assert allowed({"main", "pumps", "meters", "valves", "tank"}, {2027: 400, 2028: 300, 2029: 400}, 0.1) is False


def test_a_year_may_lend_to_the_year_before_and_borrow_from_the_year_after():
    plan = {"main", "pumps", "meters", "tank"}                 # spends 400, 350 and 120
    # 2027 takes 40 of 2028's money; 2028 makes up for it with 40 of 2029's.
    assert allowed(plan, {2027: 360, 2028: 350, 2029: 400}, 0.2) is True
    assert allowed(plan, {2027: 360, 2028: 350, 2029: 150}, 0.2) is False     # 2028 may take only 30
