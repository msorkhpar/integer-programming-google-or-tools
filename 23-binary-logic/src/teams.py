"""Lesson 6.1.1: OR-Tools' assignment with teams of workers, where the team rule is a counting row.

Six workers in two teams, four tasks. Each worker takes at most one task and each task gets exactly
one worker; each team may take at most two tasks. The team rule counts binaries over a group.
"""
# Adapted from the OR-Tools example assignment_teams_mip.py, https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/assignment_teams_mip.py

from ortools.math_opt.python import mathopt

from selection_model import EXACT, solve_highs

COSTS = [
    [90, 76, 75, 70],
    [35, 85, 55, 65],
    [125, 95, 90, 105],
    [45, 110, 95, 115],
    [60, 105, 80, 75],
    [45, 65, 110, 95],
]
TEAMS = {"team 1": [0, 2, 4], "team 2": [1, 3, 5]}
TEAM_MAX = 2


def solve(team_max: int | None) -> tuple[str, float | None, dict[str, int], list[tuple[int, int]]]:
    """The cheapest assignment: its status, cost, tasks per team and (worker, task) pairs."""
    model = mathopt.Model(name="assignment_teams")
    workers, tasks = range(len(COSTS)), range(len(COSTS[0]))
    x = {(w, t): model.add_binary_variable(name=f"x_{w}_{t}") for w in workers for t in tasks}
    for w in workers:
        model.add_linear_constraint(sum(x[w, t] for t in tasks) <= 1, name=f"worker_{w}")
    for t in tasks:
        model.add_linear_constraint(sum(x[w, t] for w in workers) == 1, name=f"task_{t}")
    tasks_of = {team: sum(x[w, t] for w in members for t in tasks) for team, members in TEAMS.items()}
    if team_max is not None:
        for team, count in tasks_of.items():
            model.add_linear_constraint(count <= team_max, name=f"cap_{team.replace(' ', '')}")
    model.minimize(sum(COSTS[w][t] * x[w, t] for w in workers for t in tasks))
    result = solve_highs(model, EXACT)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return result.termination.reason.name, None, {}, []
    values = result.variable_values()
    pairs = [(w, t) for (w, t), v in x.items() if values[v] > 0.5]
    counts = {team: round(mathopt.evaluate_expression(count, values)) for team, count in tasks_of.items()}
    return "OPTIMAL", result.objective_value(), counts, pairs


for team_max in (None, TEAM_MAX):
    status, cost, counts, pairs = solve(team_max)
    rule = "no team rule      " if team_max is None else f"each team <= {team_max}    "
    if cost is None:
        print(f"{rule}{status}")
    else:
        print(f"{rule}cost {cost:.0f}  tasks per team {counts}  (worker, task) {pairs}")
