from ortools.math_opt.python import mathopt

from cap import add_risk_caps

BASE = {2027: 500, 2028: 560, 2029: 620}
# Risk removed in each year by each (project, start year): a line rebuild A, a breaker swap B and a
# vegetation clearing C, which takes effect in the year it is done.
CUT = {
    ("A", 2027): {2027: 0, 2028: 120, 2029: 130},
    ("A", 2028): {2027: 0, 2028: 0, 2029: 140},
    ("B", 2028): {2027: 0, 2028: 0, 2029: 200},
    ("C", 2027): {2027: 40, 2028: 60, 2029: 65},
    ("C", 2029): {2027: 0, 2028: 0, 2029: 30},
}


def allowed(plan: set, cap: dict) -> bool:
    model = mathopt.Model()
    x = {key: model.add_binary_variable(name=f"x_{key[0]}_{key[1]}") for key in CUT}
    for project in {key[0] for key in CUT}:
        model.add_linear_constraint(sum(v for key, v in x.items() if key[0] == project) <= 1)
    add_risk_caps(model, x, BASE, CUT, cap)
    for key, var in x.items():
        value = 1.0 if key in plan else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_with_no_work_caps_at_base_risk_hold_and_a_lower_cap_breaks():
    assert allowed(set(), dict(BASE)) is True
    assert allowed(set(), {2027: 500, 2028: 540, 2029: 620}) is False


def test_every_year_is_held_to_its_own_cap():
    cap = {2027: 520, 2028: 500, 2029: 400}
    assert allowed({("A", 2027), ("B", 2028)}, cap) is True
    assert allowed({("A", 2028), ("B", 2028)}, cap) is False


def test_a_project_keeps_removing_risk_in_later_years():
    cap = {2027: 500, 2028: 450, 2029: 500}
    assert allowed({("A", 2027)}, cap) is True
    assert allowed(set(), cap) is False


def test_risk_removed_lowers_the_remaining_risk():
    cap = {2027: 470, 2028: 400, 2029: 450}
    assert allowed({("A", 2027), ("C", 2027)}, cap) is True
    assert allowed(set(), cap) is False


def test_the_last_year_is_capped_too():
    cap = {2027: 500, 2028: 450, 2029: 480}
    assert allowed({("A", 2027), ("B", 2028)}, cap) is True
    assert allowed({("A", 2027)}, cap) is False
