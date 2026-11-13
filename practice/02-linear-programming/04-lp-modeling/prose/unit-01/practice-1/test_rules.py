from ortools.math_opt.python import mathopt

from rules import add_share_rules

MODES = ("bus", "rail", "ferry")


def allowed(plan: dict[str, float], max_share: float, pairs: list) -> bool:
    """Fix every amount to the plan's value and ask GLOP whether the rows allow it."""
    model = mathopt.Model()
    spend = {k: model.add_variable(lb=plan[k], ub=plan[k], name=k) for k in MODES}
    add_share_rules(model, spend, max_share, pairs)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_balanced_split_is_allowed_and_one_mode_above_its_share_is_refused():
    assert allowed({"bus": 36, "rail": 32, "ferry": 32}, 0.6, []) is True
    assert allowed({"bus": 70, "rail": 20, "ferry": 10}, 0.6, []) is False


def test_a_mode_exactly_at_its_share_of_the_whole_total_is_allowed():
    assert allowed({"bus": 60, "rail": 30, "ferry": 30}, 0.5, []) is True
    assert allowed({"bus": 61, "rail": 30, "ferry": 29}, 0.5, []) is False


def test_every_mode_is_held_to_the_share_not_only_the_first():
    assert allowed({"bus": 10, "rail": 20, "ferry": 70}, 0.5, []) is False
    assert allowed({"bus": 10, "rail": 70, "ferry": 20}, 0.5, []) is False


def test_the_first_mode_of_a_pair_gets_at_least_ratio_times_the_second():
    pairs = [("rail", "ferry", 2.0)]
    assert allowed({"bus": 40, "rail": 40, "ferry": 20}, 0.5, pairs) is True
    assert allowed({"bus": 45, "rail": 30, "ferry": 25}, 0.5, pairs) is False


def test_a_pair_holds_even_when_the_second_mode_gets_more_than_the_first():
    pairs = [("bus", "rail", 0.5)]
    assert allowed({"bus": 25, "rail": 45, "ferry": 30}, 0.5, pairs) is True
    assert allowed({"bus": 20, "rail": 45, "ferry": 35}, 0.5, pairs) is False
