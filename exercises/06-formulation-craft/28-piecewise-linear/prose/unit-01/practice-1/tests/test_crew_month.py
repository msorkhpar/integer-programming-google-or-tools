from ortools.math_opt.python import mathopt

from crew_month import Job, build

# A water utility's main repairs, not the lesson's portfolio. Hours: 100, 50, 20, 25, 40, 10, 30.
JOBS = [Job("J1", 100), Job("J2", 50), Job("J3", 20), Job("J4", 25), Job("J5", 40), Job("J6", 10), Job("J7", 30)]
TIERS = [(160, 60.0), (200, 90.0), (240, 120.0)]


def allowed(plan: set[str], budget: float, tiers=TIERS) -> bool:
    """Fix which jobs are done, and ask whether the model accepts the month."""
    model, x = build(JOBS, tiers, budget)
    for jid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if jid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_month_within_the_labor_budget_is_allowed():
    assert allowed({"J1", "J2"}, 12_000) is True                       # 150 h: $9,000
    assert allowed({"J1", "J2", "J3", "J5"}, 12_000) is False          # 210 h: $14,400


def test_no_month_goes_past_the_last_tier():
    assert allowed({"J1", "J2", "J5", "J6", "J7"}, 100_000) is True    # 230 h
    assert allowed({"J1", "J2", "J3", "J5", "J6", "J7"}, 100_000) is False   # 250 h
    assert allowed({"J1", "J2"}, 100_000, [(120, 60.0), (140, 90.0)]) is False   # 150 h, other tiers


def test_overtime_hours_cost_more_than_regular_ones():
    assert allowed({"J1", "J2", "J3"}, 12_000) is True                 # 170 h: $10,500
    assert allowed({"J1", "J2", "J3", "J4"}, 12_000) is False          # 195 h: $12,750, at $60 only $11,700


def test_the_top_rate_starts_where_the_second_tier_ends():
    assert allowed({"J1", "J2", "J3", "J5", "J6"}, 16_000) is True     # 220 h: $15,600
    assert allowed({"J1", "J2", "J5", "J6", "J7"}, 16_000) is False    # 230 h: $16,800
