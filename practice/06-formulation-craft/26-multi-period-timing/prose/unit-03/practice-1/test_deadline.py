from ortools.math_opt.python import mathopt

from deadline import Project, add_aggregated_deadline, add_deadline_rows, start_variables

BYPASS_YEARS = (2027, 2028, 2029)
REPLACEMENT_YEARS = (2027, 2028, 2029, 2030)


def allowed(schedule: dict[str, int], within: int,
            bypass_years=BYPASS_YEARS, replacement_years=REPLACEMENT_YEARS) -> bool:
    bypass, replacement = Project("BY", bypass_years), Project("RP", replacement_years)
    model = mathopt.Model()
    x = start_variables(model, [bypass, replacement])
    for p in (bypass, replacement):
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1)
    add_deadline_rows(model, x, bypass, replacement, within)
    for (pid, t), var in x.items():
        value = 1.0 if schedule.get(pid) == t else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_an_on_time_replacement_is_allowed_and_a_late_one_refused():
    assert allowed({"BY": 2027, "RP": 2028}, within=2) is True
    assert allowed({"BY": 2027, "RP": 2030}, within=1) is False


def test_the_replacement_may_start_exactly_at_the_deadline():
    assert allowed({"BY": 2028, "RP": 2030}, within=2) is True
    assert allowed({"BY": 2027, "RP": 2030}, within=1) is False


def test_one_year_past_the_deadline_is_refused():
    assert allowed({"BY": 2027, "RP": 2028}, within=1) is True
    assert allowed({"BY": 2027, "RP": 2029}, within=1) is False


def test_a_bypass_needs_its_replacement():
    assert allowed({}, within=2) is True
    assert allowed({"BY": 2027}, within=2) is False


def test_the_replacement_never_comes_first():
    assert allowed({"BY": 2028, "RP": 2028}, within=1) is True
    assert allowed({"BY": 2028, "RP": 2027}, within=1) is False
    assert allowed({"RP": 2028}, within=1) is False


def test_a_bypass_too_late_for_any_replacement_is_refused():
    late = {"bypass_years": (2027, 2028, 2029, 2030), "replacement_years": (2027, 2028, 2029)}
    assert allowed({"BY": 2029, "RP": 2029}, within=1, **late) is True
    assert allowed({"BY": 2030}, within=1, **late) is False


# A small budgeted LP on which the two ways of writing the rule give different bounds.
VALUES = {("BY", 2027): 13, ("BY", 2028): 12, ("BY", 2029): 50,
          ("RP", 2027): 4, ("RP", 2028): 40, ("RP", 2029): 10, ("RP", 2030): 12}
COSTS = {"BY": 100, "RP": 60}
BUDGETS = {2027: 100, 2028: 100, 2029: 100, 2030: 40}


def lp_bound(rule) -> float:
    bypass, replacement = Project("BY", BYPASS_YEARS), Project("RP", REPLACEMENT_YEARS)
    model = mathopt.Model()
    x = start_variables(model, [bypass, replacement], integer=False)
    for p in (bypass, replacement):
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1)
    for year, budget in BUDGETS.items():
        model.add_linear_constraint(sum(COSTS[pid] * var for (pid, t), var in x.items() if t == year) <= budget)
    rule(model, x, bypass, replacement, 1)
    model.maximize(sum(VALUES[key] * var for key, var in x.items()))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_the_year_by_year_rows_give_a_tighter_bound_than_the_colleagues():
    assert lp_bound(add_deadline_rows) < lp_bound(add_aggregated_deadline) - 1
