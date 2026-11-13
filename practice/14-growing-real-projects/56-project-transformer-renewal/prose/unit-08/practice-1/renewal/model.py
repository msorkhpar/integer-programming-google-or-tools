"""The MathOpt model: when to replace each candidate transformer, within each year's budget,
with one outage per substation and year that has replacements, crews per region, and spares for
units needed sooner than a new one can be delivered.

Built for fleets of thousands: every group is indexed once, and the objective's coefficients come
from one array computation (risk.risk_table).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from .fleet import FIRST_YEAR, KINDS, REGIONS, Transformer
from .request import BASE, Request
from .risk import risk_table


@dataclass
class Built:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]      # x[i, t] = 1: replace transformer i in year t
    budget: dict[int, mathopt.LinearConstraint]     # one row per year
    out: dict[tuple[str, int], mathopt.Variable] = field(default_factory=dict)   # out[s, t] = 1: outage


def relax(built: Built) -> Built:
    """The LP relaxation, in place: every variable continuous within its bounds."""
    for v in built.model.variables():
        v.integer = False
    return built


def candidates(fleet: list[Transformer], request: Request) -> list[Transformer]:
    return [t for t in fleet if t.age >= request.min_age]


def group(units: list[Transformer], key: Callable[[Transformer], str]) -> dict[str, list[Transformer]]:
    """Units by a key, in one pass, with the keys sorted."""
    found: dict[str, list[Transformer]] = {}
    for t in units:
        found.setdefault(key(t), []).append(t)
    return dict(sorted(found.items()))


def build(fleet: list[Transformer], request: Request) -> Built:
    model = mathopt.Model(name="renewal")
    units, years = candidates(fleet, request), request.plan_years()
    x = {(t.tid, y): model.add_binary_variable(name=f"x_{t.tid}_{y}") for t in units for y in years}
    for t in units:
        model.add_linear_constraint(mathopt.fast_sum(x[t.tid, y] for y in years) <= 1, name=f"once_{t.tid}")
    by_substation = group(units, lambda t: t.substation)
    by_region = group(units, lambda t: t.region)
    out = {}
    if request.has_outages():
        out = {(s, y): model.add_binary_variable(name=f"out_{s}_{y}") for s in by_substation for y in years}
        for s, members in by_substation.items():
            for y in years:
                if request.link == "aggregated":
                    # One row per substation and year: n_s * out[s, t] covers all its replacements.
                    model.add_linear_constraint(mathopt.fast_sum(x[t.tid, y] for t in members)
                                                <= len(members) * out[s, y], name=f"outage_{s}_{y}")
                else:
                    # One row per unit and year: the stronger form (lesson 6.7.1). Each aggregated
                    # row is the sum of these, so their LP relaxation allows less.
                    for t in members:
                        model.add_linear_constraint(x[t.tid, y] <= out[s, y], name=f"outage_{t.tid}_{y}")
        if request.outages is not None:
            for r in REGIONS:
                in_region = sorted({t.substation for t in by_region.get(r, [])})
                for y in years:
                    if in_region:
                        model.add_linear_constraint(mathopt.fast_sum(out[s, y] for s in in_region)
                                                    <= request.outages, name=f"coord_{r}_{y}")
    if request.crew_weeks is not None:
        for r in REGIONS:
            for y in years:
                if r in by_region:
                    model.add_linear_constraint(
                        mathopt.fast_sum(KINDS[t.kind].crew_weeks * x[t.tid, y] for t in by_region[r])
                        <= request.crew_weeks, name=f"crews_{r}_{y}")
    if request.lead_times:
        by_kind = group(units, lambda t: t.kind)
        for kind, k in KINDS.items():
            # Before FIRST_YEAR + lead, no unit ordered now has arrived: each such replacement uses a spare.
            early = [x[t.tid, y] for t in by_kind.get(kind, []) for y in years if y < FIRST_YEAR + k.lead_years]
            if early:
                model.add_linear_constraint(mathopt.fast_sum(early) <= request.spares.get(kind, 0),
                                            name=f"spares_{kind}")
    budget = {}
    for y in years:
        spend = mathopt.fast_sum(t.cost * x[t.tid, y] for t in units)
        if out:
            spend += request.outage_cost * mathopt.fast_sum(out[s, y] for s in by_substation)
        budget[y] = model.add_linear_constraint(spend <= request.budget, name=f"budget_{y}")
    scenarios = request.scenarios or (BASE,)
    tables = [risk_table(units, request, s) for s in scenarios]

    def removed(rr) -> mathopt.LinearSum:
        return mathopt.fast_sum(rr[i, j] * x[t.tid, y] for i, t in enumerate(units) for j, y in enumerate(years))

    if request.objective == "worst":
        # Max-min: `worst` can be no more than what the plan removes under any scenario. Its upper
        # bound is what every unit at its best year would remove in the least generous scenario.
        most = min(float(rr.clip(min=0.0).max(axis=1, initial=0.0).sum()) for rr in tables)
        worst = model.add_variable(lb=0.0, ub=most, name="worst")
        for s, rr in zip(scenarios, tables):
            model.add_linear_constraint(worst <= removed(rr), name=f"worst_{s.name}")
        model.maximize(worst)
    else:
        total = sum(s.weight for s in scenarios)
        model.maximize(removed(sum(s.weight / total * rr for s, rr in zip(scenarios, tables))))
    return Built(model, x, budget, out)
