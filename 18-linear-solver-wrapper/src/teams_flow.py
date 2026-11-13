"""Lesson 4.7.4: assignment with teams, as a min-cost flow with a node per team, checked by a MIP.

Adapted from the OR-Tools example balance_min_flow.py,
https://github.com/google/or-tools/blob/stable/ortools/graph/samples/balance_min_flow.py
(Apache-2.0): six workers in two teams, four tasks, and each team takes at most two tasks.
"""

from ortools.graph.python import linear_sum_assignment, min_cost_flow
from ortools.math_opt.python import mathopt

COSTS = [[90, 76, 75, 70], [35, 85, 55, 65], [125, 95, 90, 105],
         [45, 110, 95, 115], [60, 105, 80, 75], [45, 65, 110, 95]]
TEAMS = {"A": [0, 2, 4], "B": [1, 3, 5]}
MAX_PER_TEAM = 2
workers, tasks = len(COSTS), len(COSTS[0])

# Without the team rule: plain assignment, squared with two dummy tasks of cost 0.
plain = linear_sum_assignment.SimpleLinearSumAssignment()
for w in range(workers):
    for t, c in enumerate(COSTS[w] + [0] * (workers - tasks)):
        plain.add_arc_with_cost(w, t, c)
plain.solve()
chosen = [w for w in range(workers) if plain.right_mate(w) < tasks]
print(f"no team rule: cost {plain.optimal_cost()}, workers {chosen}, "
      f"team A takes {sum(w in TEAMS['A'] for w in chosen)}")

# Nodes: 0 source; 1..6 workers; 7..10 tasks; 11, 12 the teams; 13 sink.
SOURCE, SINK = 0, 13
worker_node = {w: 1 + w for w in range(workers)}
task_node = {t: 1 + workers + t for t in range(tasks)}
team_node = {"A": 11, "B": 12}

smcf = min_cost_flow.SimpleMinCostFlow()
for team, members in TEAMS.items():
    smcf.add_arc_with_capacity_and_unit_cost(SOURCE, team_node[team], MAX_PER_TEAM, 0)  # the team rule
    for w in members:
        smcf.add_arc_with_capacity_and_unit_cost(team_node[team], worker_node[w], 1, 0)  # one task per worker
work = {}
for w in range(workers):
    for t in range(tasks):
        work[w, t] = smcf.add_arc_with_capacity_and_unit_cost(worker_node[w], task_node[t], 1, COSTS[w][t])
for t in range(tasks):
    smcf.add_arc_with_capacity_and_unit_cost(task_node[t], SINK, 1, 0)                   # one worker per task
smcf.set_node_supply(SOURCE, tasks)
smcf.set_node_supply(SINK, -tasks)

status = smcf.solve()
print(f"min-cost flow: {status.name}, cost {smcf.optimal_cost()}")
for (w, t), arc in work.items():
    if smcf.flow(arc) > 0:
        team = next(name for name, members in TEAMS.items() if w in members)
        print(f"  worker {w} (team {team}) -> task {t}, cost {COSTS[w][t]}")

model = mathopt.Model(name="teams")
x = {(w, t): model.add_binary_variable(name=f"x_{w}_{t}") for w in range(workers) for t in range(tasks)}
for w in range(workers):
    model.add_linear_constraint(sum(x[w, t] for t in range(tasks)) <= 1, name=f"worker_{w}")
for t in range(tasks):
    model.add_linear_constraint(sum(x[w, t] for w in range(workers)) == 1, name=f"task_{t}")
for team, members in TEAMS.items():
    model.add_linear_constraint(sum(x[w, t] for w in members for t in range(tasks)) <= MAX_PER_TEAM,
                                name=f"team_{team}")
model.minimize(sum(COSTS[w][t] * x[w, t] for w, t in x))
print(f"MIP with team rows: cost {mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value():.0f}")
