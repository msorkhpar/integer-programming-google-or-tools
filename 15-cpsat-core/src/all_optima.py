"""Lesson 4.4.3: every optimal plan, found in two solves: optimize, then enumerate at the optimum.

The collector is adapted from the OR-Tools example search_for_all_solutions_sample_sat.py,
https://github.com/google/or-tools/blob/stable/ortools/sat/samples (Apache-2.0). GridCap is a
fictional utility's portfolio; the scores are invented for the course.
"""

import itertools

from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import groups_of, one_worker, selection

UNIT = 500     # the committee scores each project in points of $500k of NPV, rounded


class PlanCollector(cp_model.CpSolverSolutionCallback):
    """Keep the set of funded projects of every solution the solver reports."""

    def __init__(self, x: dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.plans = []

    def on_solution_callback(self) -> None:
        self.plans.append(tuple(i for i, v in self.x.items() if self.boolean_value(v)))


def all_optimal_plans(portfolio) -> tuple[int, list[tuple[str, ...]], str, int]:
    """The best score, every plan that reaches it, the enumeration's status and how many solutions it reported."""
    points = {p.project_id: round(p.value / UNIT) for p in portfolio.projects}
    sel = selection(portfolio, native=True)
    sel.model.add(sel.k == 0)                                  # no borrowing in this question
    score = sum(points[i] * v for i, v in sel.x.items())
    sel.model.maximize(score)

    solver = one_worker()                                      # solve 1: the best score
    if solver.solve(sel.model) != cp_model.OPTIMAL:
        raise RuntimeError("no proven optimum to enumerate at")
    best = round(solver.objective_value)

    sel.model.add(score == best)                               # solve 2: every plan with that score
    sel.model.clear_objective()
    collector = PlanCollector(sel.x)
    solver = one_worker()
    solver.parameters.enumerate_all_solutions = True
    status = solver.solve(sel.model, collector)
    return best, sorted(set(collector.plans)), solver.status_name(status), len(collector.plans)


small = generate("small")
best, plans, status, reported = all_optimal_plans(small)
print(f"enumeration {status}, {reported} solutions reported")
common = set.intersection(*map(set, plans))
print(f"GridCap small: best score {best} points, {len(plans)} optimal plans; all share {len(common)} projects")
for plan in plans:
    npv = sum(small.project(i).value for i in plan)
    capex = sum(small.project(i).capex for i in plan)
    print(f"  + {' '.join(sorted(set(plan) - common)):30} NPV ${npv:,}k  capex ${capex:,}k")

tiny = generate("tiny")
best, plans, status, reported = all_optimal_plans(tiny)
points = {p.project_id: round(p.value / UNIT) for p in tiny.projects}
groups = groups_of(tiny)


def allowed(plan: set) -> bool:
    return (sum(tiny.project(i).capex for i in plan) <= tiny.capital_budget
            and all(p.project_id in plan for p in tiny.projects if p.must_do)
            and all(p.parent in plan for p in tiny.projects if p.parent and p.project_id in plan)
            and all(len(plan & set(g)) <= 1 for g in groups.values())
            and all(sum(c.crew_months * c.duration for c in tiny.projects if c.program == g and c.project_id in plan)
                    <= sum(tiny.crews[g, y] for y in tiny.years) for g in {p.program for p in tiny.projects}))


ids = [p.project_id for p in tiny.projects]
every = [set(c) for r in range(len(ids) + 1) for c in itertools.combinations(ids, r) if allowed(set(c))]
top = max(sum(points[i] for i in plan) for plan in every)
brute = sorted(tuple(sorted(plan)) for plan in every if sum(points[i] for i in plan) == top)
print(f"GridCap tiny: {len(plans)} optimal plans; checking all {2 ** len(ids)} subsets finds {len(brute)}, same: {brute == plans}")

sel = selection(small, native=True)
sel.model.add(sel.k == 0)
sel.model.maximize(sum(round(p.value / UNIT) * sel.x[p.project_id] for p in small.projects))
collector = PlanCollector(sel.x)
solver = one_worker()
solver.parameters.enumerate_all_solutions = True
status = solver.solve(sel.model, collector)
print(f"objective left on: {solver.status_name(status)}, {len(collector.plans)} solutions reported")
