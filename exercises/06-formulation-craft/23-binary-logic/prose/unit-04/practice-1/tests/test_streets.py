from ortools.math_opt.python import mathopt

from streets import Street, build

# A city's street works, not the lesson's portfolio.
STREETS = [Street("S1", 100), Street("S2", 80), Street("S3", 60), Street("S4", 50), Street("S5", 40),
           Street("N1", 30)]
DETOURS = {("S1", "S2"): 30}
CORRIDORS = [(["S3", "S4", "S5"], 25)]


def allowed(plan: set[str], budget: int) -> bool:
    """Fix which streets are rebuilt and ask whether the model accepts the plan."""
    model, x = build(STREETS, DETOURS, CORRIDORS, budget)
    for sid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if sid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_detour_is_paid_when_both_streets_are_rebuilt():
    assert allowed({"S1", "S2"}, budget=220) is True           # 180 + 30 = 210
    assert allowed({"S1", "S2", "N1"}, budget=220) is False    # 210 + 30 = 240


def test_a_corridor_fee_is_paid_when_every_street_of_it_is_rebuilt():
    assert allowed({"S3", "S4", "S5"}, budget=180) is True         # 150 + 25 = 175
    assert allowed({"S3", "S4", "S5", "N1"}, budget=180) is False  # 180 + 25 = 205


def test_one_street_of_a_pair_needs_no_detour():
    assert allowed({"S1"}, budget=110) is True                 # 100
    assert allowed({"S1", "N1"}, budget=110) is False          # 130


def test_part_of_a_corridor_pays_no_corridor_fee():
    assert allowed({"S3", "S4"}, budget=120) is True           # 110
    assert allowed({"S3", "S4", "N1"}, budget=120) is False    # 140
