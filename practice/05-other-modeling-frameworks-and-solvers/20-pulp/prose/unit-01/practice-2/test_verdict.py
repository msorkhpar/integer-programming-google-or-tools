import pulp

from verdict import report


def depot_problem(trucks: int):
    """A bus operator's depot upgrades: maximize seats added with `trucks` delivery trucks."""
    prob = pulp.LpProblem("depots", pulp.LpMaximize)
    d = {k: prob.add_variable(f"d_{k}", 0, 1, cat=pulp.LpBinary) for k in ("north", "south", "east")}
    prob += 40 * d["north"] + 30 * d["south"] + 25 * d["east"], "seats"
    prob += 2 * d["north"] + 1 * d["south"] + 1 * d["east"] <= trucks, "trucks"
    return prob, d


def solved(prob):
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    return prob


def test_a_finished_search_is_proved_with_its_value():
    prob, _ = depot_problem(trucks=3)
    assert report(solved(prob)) == ("proved", 70)


def test_a_larger_fleet_gives_a_larger_proved_value():
    prob, _ = depot_problem(trucks=4)
    assert report(solved(prob)) == ("proved", 95)


def test_a_search_stopped_early_is_reported_unproved():
    prob, _ = depot_problem(trucks=3)
    solved(prob)
    # What CBC's interface leaves when a time or node limit stops the search with a plan in hand
    # (lesson 5.2.1 shows it on GridCap): status Optimal, sol_status "Solution Found".
    prob.sol_status = pulp.LpSolutionIntegerFeasible
    assert prob.status == pulp.LpStatusOptimal
    assert report(prob) == ("unproved", 70)


def test_an_infeasible_model_has_no_plan_even_with_values_left_behind():
    prob, d = depot_problem(trucks=3)
    prob += d["north"] + d["south"] + d["east"] >= 4, "all_four"
    solved(prob)
    assert prob.status == pulp.LpStatusInfeasible
    assert report(prob) == ("no plan", None)


def test_an_unbounded_model_has_no_plan():
    prob = pulp.LpProblem("open", pulp.LpMaximize)
    hours = prob.add_variable("overtime_hours", 0, None)
    prob += hours, "paid"
    solved(prob)
    assert prob.status == pulp.LpStatusUnbounded
    assert report(prob) == ("no plan", None)
