from ortools.math_opt.python import mathopt

from fleet import build

# A storm-response team's identical rented units (not GridCap); each unit is rented for 30 days.
DAYS = {"S0": 16, "S1": 14, "S2": 12, "S3": 9, "S4": 8, "S5": 7}


def allowed(days, units, served_by: dict, rented: set) -> bool:
    fleet = build(days, units, ordered=True)
    for (s, k), var in fleet.x.items():
        var.lower_bound = var.upper_bound = 1.0 if served_by[s] == k else 0.0
    for k, var in fleet.y.items():
        var.lower_bound = var.upper_bound = 1.0 if k in rented else 0.0
    return mathopt.solve(fleet.model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def best(days, units, ordered) -> float:
    return mathopt.solve(build(days, units, ordered=ordered).model, mathopt.SolverType.HIGHS,
                         params=mathopt.SolveParameters(relative_gap_tolerance=0.0)).objective_value()


def test_the_rows_keep_the_fewest_units_and_a_plan_numbered_in_order():
    assert best(DAYS, 5, ordered=True) == best(DAYS, 5, ordered=False) == 3
    # Unit 0 takes S0 and S1 (30 days), unit 1 takes S2, S3 and S4 (29), unit 2 takes S5.
    plan = {"S0": 0, "S1": 0, "S2": 1, "S3": 1, "S4": 1, "S5": 2}
    assert allowed(DAYS, 5, plan, {0, 1, 2}) is True
    # The same plan moved up one unit: unit 0 is idle and site S0 is on unit 1.
    shifted = {s: k + 1 for s, k in plan.items()}
    assert allowed(DAYS, 5, shifted, {1, 2, 3}) is False


def test_a_unit_is_rented_only_after_the_one_before_it():
    plan = {"S0": 0, "S1": 0, "S2": 1, "S3": 1, "S4": 1, "S5": 1}
    days = {**DAYS, "S5": 1}
    assert allowed(days, 5, plan, {0, 1}) is True
    assert allowed(days, 5, {**plan, "S2": 2, "S3": 2, "S4": 2, "S5": 2}, {0, 2}) is False


def test_site_number_n_goes_to_one_of_the_first_n_plus_one_units():
    plan = {"S0": 0, "S1": 0, "S2": 1, "S3": 1, "S4": 1, "S5": 2}
    assert allowed(DAYS, 5, plan, {0, 1, 2}) is True
    # Units 0 and 1 swapped: S0, the first site, would be on unit 1.
    assert allowed(DAYS, 5, {**plan, "S0": 1, "S1": 1, "S2": 0, "S3": 0, "S4": 0}, {0, 1, 2}) is False


def test_a_lighter_first_unit_stays_allowed():
    # Numbered by first site, unit 0 may carry fewer days than unit 1: A on unit 0, B and C on unit 1.
    days = {"A": 5, "B": 20, "C": 9}
    assert allowed(days, 3, {"A": 0, "B": 1, "C": 1}, {0, 1}) is True
    assert allowed(days, 3, {"A": 1, "B": 0, "C": 0}, {0, 1}) is False
