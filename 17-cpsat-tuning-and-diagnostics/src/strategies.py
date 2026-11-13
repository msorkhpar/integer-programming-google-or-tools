"""Lesson 4.6.1: the same GridCap medium model under each search branching, one worker, same budget.

GridCap is a fictional utility's portfolio. With one worker the search is a single sequence of
decisions, so every number below repeats from run to run.
"""

from ortools.sat.python import cp_model

from cpsat_plan import build
from gridcap import generate

medium = generate("medium")


class FirstAndCount(cp_model.CpSolverSolutionCallback):
    """Records the first plan's objective and counts the improving plans."""

    def __init__(self) -> None:
        super().__init__()
        self.first = None
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        if self.first is None:
            self.first = self.objective_value


def run(branching, greedy_order: bool = False) -> None:
    plan = build(medium)
    if greedy_order:
        # Branch on the start variables in falling NPV order, and try 1 (start it) first.
        order = sorted(plan.x, key=lambda key: -medium.project(key[0]).npv[key[1]])
        plan.model.add_decision_strategy([plan.x[key] for key in order],
                                         cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_deterministic_time = 2.0
    solver.parameters.search_branching = branching
    seen = FirstAndCount()
    solver.solve(plan.model, seen)
    label = branching.name + (" + NPV order" if greedy_order else "")
    print(f"{label:<32} first ${seen.first:>9,.0f}k  plans {seen.count:>2}  "
          f"best ${solver.objective_value:>9,.0f}k  bound ${solver.best_objective_bound:>9,.0f}k")


for branching in (cp_model.AUTOMATIC_SEARCH, cp_model.LP_SEARCH, cp_model.PSEUDO_COST_SEARCH,
                  cp_model.PORTFOLIO_SEARCH):
    run(branching)
run(cp_model.FIXED_SEARCH, greedy_order=True)
run(cp_model.AUTOMATIC_SEARCH, greedy_order=True)
