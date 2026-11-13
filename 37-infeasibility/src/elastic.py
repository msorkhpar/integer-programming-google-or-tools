"""Lesson 9.1.4: elastic rows in MathOpt, the same feasibility relaxation gurobipy's feasRelax builds.

`elastic` copies a model and gives each soft row two nonnegative elastic variables, one per side
that has a bound: `over` lets the row exceed its upper bound, `under` lets it fall short of its
lower bound. Hard rows stay as they are. Three objectives use them:

* `min_violation`: minimize the weighted sum of elastic amounts (feasRelax's relaxobjtype 0);
* `fewest_rules`: minimize the number of rows that bend, with a 0/1 `bent` variable per soft row
  (relaxobjtype 2);
* `best_repair`: among the repairs of least weighted violation, the plan of greatest NPV
  (feasRelax with minrelax=True), as a second solve with the violation capped at the first one's.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from lock_model import solve


@dataclass
class Elastic:
    model: mathopt.Model
    weight: dict[str, float]                                        # soft row -> cost per unit of violation
    over: dict[str, mathopt.Variable] = field(default_factory=dict)  # row may exceed its upper bound by this
    under: dict[str, mathopt.Variable] = field(default_factory=dict) # row may fall short of its lower bound by this
    goal: mathopt.LinearExpression = field(default_factory=mathopt.LinearExpression)   # the model's own objective

    def violation(self) -> mathopt.LinearExpression:
        return mathopt.fast_sum(self.weight[n] * e for side in (self.over, self.under) for n, e in side.items())

    def bends(self, result: mathopt.SolveResult) -> dict[str, float]:
        """Each soft row that bent, and by how much (positive: over the upper bound; negative: under the lower)."""
        values = result.variable_values()
        bent = {}
        for name in self.weight:
            amount = values.get(self.over.get(name), 0.0) - values.get(self.under.get(name), 0.0)
            if abs(amount) > 1e-6:
                bent[name] = round(amount, 6)
        return bent


def elastic(model: mathopt.Model, weight: dict[str, float]) -> Elastic:
    """A copy of `model` in which every row named in `weight` may bend, at that cost per unit."""
    work = mathopt.Model.from_model_proto(model.export_model())
    goal = mathopt.fast_sum(t.coefficient * t.variable for t in work.objective.linear_terms())
    el = Elastic(work, dict(weight), goal=goal)
    for row in work.linear_constraints():
        if row.name not in weight:
            continue
        if not math.isinf(row.upper_bound):
            el.over[row.name] = work.add_variable(lb=0, name=f"over_{row.name}")
            row.set_coefficient(el.over[row.name], -1.0)            # a.x - over <= upper
        if not math.isinf(row.lower_bound):
            el.under[row.name] = work.add_variable(lb=0, name=f"under_{row.name}")
            row.set_coefficient(el.under[row.name], 1.0)            # a.x + under >= lower
    return el


def min_violation(el: Elastic) -> mathopt.SolveResult:
    el.model.minimize(el.violation())
    return solve(el.model)


def fewest_rules(el: Elastic, big: dict[str, float]) -> mathopt.SolveResult:
    """Fewest soft rows bent; `big[name]` bounds how far that row may bend (its elastic's upper bound)."""
    bent = {}
    for name in el.weight:
        bent[name] = el.model.add_binary_variable(name=f"bent_{name}")
        for side in (el.over, el.under):
            if name in side:
                el.model.add_linear_constraint(side[name] <= big[name] * bent[name], name=f"link_{side[name].name}")
    el.model.minimize(mathopt.fast_sum(bent.values()))
    return solve(el.model)


def best_repair(el: Elastic, least: float) -> mathopt.SolveResult:
    """The model's own objective (maximized) among repairs whose weighted violation is at most `least`."""
    el.model.add_linear_constraint(el.violation() <= least + 1e-6, name="least_violation")
    el.model.maximize(el.goal)
    return solve(el.model)
