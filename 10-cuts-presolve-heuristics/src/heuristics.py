"""Primal heuristics for a 0-1 maximization model: rounding, greedy fill, diving and RINS.

Each works on the LP relaxation of a MathOpt model whose variables all have bounds [0, 1], and
checks plans against the model's rows read into a `BinaryModel` (presolve.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from presolve import BinaryModel, from_selection
from selection import solve_quiet

EPS = 1e-6


def broken(m: BinaryModel, plan: dict[str, int]) -> list[str]:
    """The rows a 0-1 plan breaks."""
    out = []
    for name, row in m.rows.items():
        lhs = sum(a * plan[j] for j, a in row.coefs.items())
        if lhs > row.rhs + EPS or (row.sense == "==" and lhs < row.rhs - EPS):
            out.append(name)
    return out


def value(m: BinaryModel, plan: dict[str, int]) -> float:
    return sum(c * plan[j] for j, c in m.objective.items())


class Relaxation:
    """The model's LP relaxation, re-solved with some variables fixed (GLOP)."""

    def __init__(self, model: mathopt.Model):
        self.model = model
        self.x = {v.name: v for v in model.variables()}
        for v in self.x.values():
            v.integer = False

    def solve(self, fixed: dict[str, int] | None = None) -> tuple[float | None, dict[str, float]]:
        fixed = fixed or {}
        for j, v in self.x.items():
            v.lower_bound, v.upper_bound = (fixed[j], fixed[j]) if j in fixed else (0.0, 1.0)
        result = mathopt.solve(self.model, mathopt.SolverType.GLOP)
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            return None, {}
        return result.objective_value(), {j: result.variable_values(v) for j, v in self.x.items()}


def fractional(x: dict[str, float]) -> list[str]:
    return [j for j, v in x.items() if EPS < v < 1 - EPS]


def round_down(x: dict[str, float]) -> dict[str, int]:
    return {j: int(v > 1 - EPS) for j, v in x.items()}


def round_nearest(x: dict[str, float]) -> dict[str, int]:
    return {j: int(v >= 0.5) for j, v in x.items()}


def greedy_fill(m: BinaryModel, plan: dict[str, int], weight: dict[str, float]) -> dict[str, int]:
    """Add unfunded projects, best value per unit of `weight` first, whenever the plan stays feasible."""
    plan = dict(plan)
    for j in sorted((j for j in plan if not plan[j]), key=lambda j: (-m.objective[j] / max(weight[j], 1), j)):
        plan[j] = 1
        if broken(m, plan):
            plan[j] = 0
    return plan


@dataclass
class DiveStep:
    depth: int
    variable: str
    lp_value: float
    fixed_to: int
    bound: float


def dive(lp: Relaxation, max_depth: int = 1000) -> tuple[dict[str, int] | None, list[DiveStep]]:
    """Fractional diving: round the least fractional variable to its nearest value, re-solve, repeat.

    If that fixing makes the LP infeasible, fix the variable the other way. Stops at an LP optimum
    with no fractional variable (a feasible 0-1 plan) or when both fixings fail.
    """
    fixed: dict[str, int] = {}
    steps: list[DiveStep] = []
    bound, x = lp.solve(fixed)
    for depth in range(1, max_depth + 1):
        if bound is None:
            return None, steps
        candidates = fractional(x)
        if not candidates:
            return {j: round(v) for j, v in x.items()}, steps
        j = min(candidates, key=lambda j: (min(x[j], 1 - x[j]), j))
        first = int(x[j] >= 0.5)
        for target in (first, 1 - first):
            new_bound, new_x = lp.solve({**fixed, j: target})
            if new_bound is not None:
                break
        steps.append(DiveStep(depth, j, x[j], target, new_bound if new_bound is not None else float("nan")))
        fixed[j] = target
        bound, x = new_bound, new_x
    return None, steps


def rins_fixings(incumbent: dict[str, int], x: dict[str, float]) -> dict[str, int]:
    """Where the incumbent and the LP optimum agree on a 0 or a 1, fix that value."""
    return {j: incumbent[j] for j in incumbent if abs(x[j] - incumbent[j]) < EPS}


def rins(model: mathopt.Model, incumbent: dict[str, int], x: dict[str, float]) -> tuple[dict[str, int], int]:
    """Solve the sub-MIP left after fixing every variable the incumbent and the LP agree on."""
    fix = rins_fixings(incumbent, x)
    variables = {v.name: v for v in model.variables()}
    for j, v in variables.items():
        v.integer = True
        v.lower_bound, v.upper_bound = (fix[j], fix[j]) if j in fix else (0.0, 1.0)
    result = solve_quiet(model, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    plan = {j: round(result.variable_values(v)) for j, v in variables.items()}
    for v in variables.values():
        v.lower_bound, v.upper_bound = 0.0, 1.0
    return plan, len(variables) - len(fix)


def rows_of(model: mathopt.Model) -> BinaryModel:
    return from_selection(model)
