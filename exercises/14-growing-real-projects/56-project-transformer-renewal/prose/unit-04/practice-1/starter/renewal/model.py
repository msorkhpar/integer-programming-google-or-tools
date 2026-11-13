"""The MathOpt model: when to replace each candidate transformer, within each year's budget,
with one outage per substation and year that has replacements."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from .fleet import REGIONS, Transformer
from .request import Request
from .risk import risk_removed


@dataclass
class Built:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]      # x[i, t] = 1: replace transformer i in year t
    budget: dict[int, mathopt.LinearConstraint]     # one row per year
    out: dict[tuple[str, int], mathopt.Variable] = field(default_factory=dict)   # out[s, t] = 1: outage


def candidates(fleet: list[Transformer], request: Request) -> list[Transformer]:
    return [t for t in fleet if t.age >= request.min_age]


def build(fleet: list[Transformer], request: Request) -> Built:
    model = mathopt.Model(name="renewal")
    units, years = candidates(fleet, request), request.plan_years()
    x = {(t.tid, y): model.add_binary_variable(name=f"x_{t.tid}_{y}") for t in units for y in years}
    for t in units:
        model.add_linear_constraint(sum(x[t.tid, y] for y in years) <= 1, name=f"once_{t.tid}")
    out = {}
    if request.has_outages():
        substations = sorted({t.substation for t in units})
        out = {(s, y): model.add_binary_variable(name=f"out_{s}_{y}") for s in substations for y in years}
        for s in substations:
            for y in years:
                members = [t for t in units if t.substation == s]
                # One row per substation and year: any replacement there needs the outage.
                model.add_linear_constraint(sum(x[t.tid, y] for t in members) <= len(members) * out[s, y],
                                            name=f"outage_{s}_{y}")
        if request.outages is not None:
            for r in REGIONS:
                in_region = sorted({t.substation for t in units if t.region == r})
                for y in years:
                    if in_region:
                        model.add_linear_constraint(sum(out[s, y] for s in in_region) <= request.outages,
                                                    name=f"coord_{r}_{y}")
    budget = {}
    for y in years:
        spend = sum(t.cost * x[t.tid, y] for t in units)
        spend += request.outage_cost * sum(v for (s, year), v in out.items() if year == y)
        budget[y] = model.add_linear_constraint(spend <= request.budget, name=f"budget_{y}")
    model.maximize(sum(risk_removed(t, y, request) * x[t.tid, y] for t in units for y in years))
    return Built(model, x, budget, out)
