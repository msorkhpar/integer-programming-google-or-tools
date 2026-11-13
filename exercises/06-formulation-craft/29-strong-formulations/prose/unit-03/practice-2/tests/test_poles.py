from ortools.math_opt.python import mathopt

from poles import build_counted, build_named

# A distribution company's feeder (not GridCap): identical poles to replace over four years.
COST = {2027: 9, 2028: 10, 2029: 11, 2030: 12}         # $k to replace one pole in that year
RISK = {2027: 3, 2028: 3, 2029: 4, 2030: 0}            # $k of risk per pole still waiting at year end
CREW = {2027: 8, 2028: 10, 2029: 10, 2030: 12}         # poles the crew can replace that year


def fixed(poles, plan, risk=RISK):
    """Solve the counted model with every count fixed to the plan; None if the plan is refused."""
    model, n = build_counted(poles, COST, risk, CREW)
    assert set(n) == set(COST), "one count variable per year"
    for y, var in n.items():
        model.add_linear_constraint(var == plan[y])        # a row, so the variables' own bounds still apply
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.objective_value() if result.termination.reason == mathopt.TerminationReason.OPTIMAL else None


def test_a_plan_within_the_crews_is_allowed_and_one_over_a_crew_is_not():
    assert fixed(20, {2027: 8, 2028: 6, 2029: 6, 2030: 0}) is not None
    assert fixed(20, {2027: 9, 2028: 5, 2029: 6, 2030: 0}) is None


def test_every_pole_is_replaced_by_the_end():
    high = {y: 20 for y in COST}            # waiting is so costly that a model allowed to skip still won't
    assert fixed(20, {2027: 8, 2028: 6, 2029: 6, 2030: 0}, high) is not None
    assert fixed(20, {2027: 8, 2028: 6, 2029: 5, 2030: 0}, high) is None


def test_the_cost_counts_every_pole_still_waiting_at_each_year_end():
    # 8 in 2027, 6 in 2028, 6 in 2029: cost 72 + 60 + 66 = 198; waiting 12, 6, 0, 0: risk 36 + 18 = 54.
    assert abs(fixed(20, {2027: 8, 2028: 6, 2029: 6, 2030: 0}) - 252) < 1e-6
    named, _ = build_named(20, COST, RISK, CREW)
    counted, _ = build_counted(20, COST, RISK, CREW)
    best = [mathopt.solve(m, mathopt.SolverType.HIGHS).objective_value() for m in (named, counted)]
    assert abs(best[0] - best[1]) < 1e-6
