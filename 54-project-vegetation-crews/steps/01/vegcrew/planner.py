"""Turn a season into a plan: a 0-1 knapsack over the circuits, solved by HiGHS through MathOpt."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from vegcrew.data import Season

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
STATUS = {mathopt.TerminationReason.OPTIMAL: "OPTIMAL", mathopt.TerminationReason.FEASIBLE: "FEASIBLE",
          mathopt.TerminationReason.INFEASIBLE: "INFEASIBLE"}


@dataclass(frozen=True)
class Trim:
    cid: str
    month: int = 0                                  # stub for lesson 14.1.2


@dataclass(frozen=True)
class Plan:
    status: str                                     # OPTIMAL, FEASIBLE, INFEASIBLE or NOT_SOLVED
    trims: dict[str, Trim] = field(default_factory=dict)
    cost: int = 0                                   # $k spent
    risk_removed: int = 0                           # $k a year of risk the trims remove


def build(season: Season) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name=f"trim_{season.name}")
    x = {c.cid: model.add_binary_variable(name=f"x_{c.cid}") for c in season.circuits}
    model.add_linear_constraint(sum(c.cost * x[c.cid] for c in season.circuits) <= season.budget,
                                name="budget")
    model.maximize(sum(c.risk * x[c.cid] for c in season.circuits))
    return model, x


def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim this year: the most risk removed within the budget."""
    model, x = build(season)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
    status = STATUS.get(result.termination.reason, result.termination.reason.name)
    if status not in ("OPTIMAL", "FEASIBLE"):
        return Plan(status)
    chosen = [c for c in season.circuits if result.variable_values(x[c.cid]) > 0.5]
    return Plan(status, {c.cid: Trim(c.cid) for c in chosen},
                cost=sum(c.cost for c in chosen), risk_removed=sum(c.risk for c in chosen))
