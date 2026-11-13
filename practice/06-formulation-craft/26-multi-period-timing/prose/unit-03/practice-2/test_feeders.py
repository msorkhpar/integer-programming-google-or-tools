from ortools.math_opt.python import mathopt

from feeders import Project, add_aggregated_needs, add_parent_rows, selection_variables

FEEDERS = ["F1", "F2", "F3", "F4"]


def allowed(plan: set[str]) -> bool:
    projects = [Project(pid, 10, 1) for pid in ["SUB", *FEEDERS]]
    model = mathopt.Model()
    x = selection_variables(model, projects)
    add_parent_rows(model, x, "SUB", FEEDERS)
    for pid, var in x.items():
        value = 1.0 if pid in plan else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_feeder_without_the_substation_is_refused():
    assert allowed(set()) is True
    assert allowed({"F1"}) is False
    assert allowed({"F4"}) is False


def test_the_substation_may_be_rebuilt_alone():
    assert allowed({"SUB", "F2"}) is True
    assert allowed({"SUB"}) is True
    assert allowed({"F2"}) is False


def test_several_feeders_may_share_the_substation():
    assert allowed({"SUB", "F1", "F3"}) is True
    assert allowed({"F1", "F3"}) is False


# A small budgeted LP: the substation is expensive, one feeder is very valuable, and no whole plan
# with a feeder fits the budget.
PROJECTS = [Project("SUB", 90, 0), Project("F1", 10, 50), Project("F2", 10, 5), Project("F3", 10, 5)]
BUDGET = 60


def lp_bound(rule) -> float:
    model = mathopt.Model()
    x = selection_variables(model, PROJECTS, integer=False)
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in PROJECTS) <= BUDGET)
    rule(model, x, "SUB", ["F1", "F2", "F3"])
    model.maximize(sum(p.value * x[p.pid] for p in PROJECTS))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_your_rows_give_a_tighter_bound_than_the_colleagues():
    assert lp_bound(add_parent_rows) < lp_bound(add_aggregated_needs) - 1
