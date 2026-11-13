"""Lesson 4.7.4: each of GridCap's eight crews leads one tiny project, by LinearSumAssignment and by a MIP.

The MIP is the assignment model (lesson 6.3.2, later in the course, generalizes it) in MathOpt; its LP relaxation is
solved too. GridCap, its crews and costs are fictional.
"""

from ortools.graph.python import linear_sum_assignment
from ortools.math_opt.python import mathopt

from crews import CREWS, cost_table
from gridcap import generate

tiny = generate("tiny")
sites = [p.project_id for p in tiny.projects]
cost = cost_table(tiny)
print(f"{len(CREWS)} crews, {len(sites)} projects, {len(cost)} allowed pairs of {len(CREWS) * len(sites)}")

# LinearSumAssignment: left nodes are crews 0..7, right nodes projects 0..7; a forbidden pair gets no arc.
lsa = linear_sum_assignment.SimpleLinearSumAssignment()
for (c, s), k in cost.items():
    lsa.add_arc_with_cost(CREWS.index(c), sites.index(s), k)
status = lsa.solve()
print(f"LinearSumAssignment: {status.name}, cost ${lsa.optimal_cost()}k")
for i, c in enumerate(CREWS):
    print(f"  {c:12} -> {sites[lsa.right_mate(i)]} ({tiny.projects[lsa.right_mate(i)].program}, "
          f"{tiny.projects[lsa.right_mate(i)].region})  ${lsa.assignment_cost(i)}k")

# The same problem as a MIP, and as its LP relaxation.
for integer in (True, False):
    model = mathopt.Model(name="crew to site")
    x = {pair: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{pair[0]}_{pair[1]}") for pair in cost}
    for c in CREWS:
        model.add_linear_constraint(sum(v for (cc, _), v in x.items() if cc == c) == 1, name=f"crew_{c}")
    for s in sites:
        model.add_linear_constraint(sum(v for (_, ss), v in x.items() if ss == s) == 1, name=f"site_{s}")
    model.minimize(sum(k * x[pair] for pair, k in cost.items()))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS if integer else mathopt.SolverType.GLOP)
    fractional = sum(1e-6 < result.variable_values(v) < 1 - 1e-6 for v in x.values())
    print(f"{'MIP (HiGHS)' if integer else 'LP relaxation (GLOP)'}: cost ${result.objective_value():,.0f}k, "
          f"fractional variables: {fractional}")
