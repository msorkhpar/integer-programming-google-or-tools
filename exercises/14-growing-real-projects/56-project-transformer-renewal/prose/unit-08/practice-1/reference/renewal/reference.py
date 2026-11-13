"""The reference builder: the model before it was built for scale, one plain loop per row family.

It is slow at scale and kept on purpose: the fast builder in model.py is correct only if it makes
exactly this model (lesson 11.1.2).
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from .fleet import FIRST_YEAR, KINDS, REGIONS, Transformer
from .model import Built, candidates
from .request import Request
from .risk import risk_removed


def build_reference(fleet: list[Transformer], request: Request) -> Built:
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
    if request.crew_weeks is not None:
        for r in REGIONS:
            for y in years:
                in_region = [t for t in units if t.region == r]
                if in_region:
                    model.add_linear_constraint(
                        sum(KINDS[t.kind].crew_weeks * x[t.tid, y] for t in in_region) <= request.crew_weeks,
                        name=f"crews_{r}_{y}")
    if request.lead_times:
        for kind, k in KINDS.items():
            # Before FIRST_YEAR + lead, no unit ordered now has arrived: each such replacement uses a spare.
            early = [x[t.tid, y] for t in units if t.kind == kind for y in years if y < FIRST_YEAR + k.lead_years]
            if early:
                model.add_linear_constraint(sum(early) <= request.spares.get(kind, 0), name=f"spares_{kind}")
    budget = {}
    for y in years:
        spend = sum(t.cost * x[t.tid, y] for t in units)
        spend += request.outage_cost * sum(v for (s, year), v in out.items() if year == y)
        budget[y] = model.add_linear_constraint(spend <= request.budget, name=f"budget_{y}")
    model.maximize(sum(risk_removed(t, y, request) * x[t.tid, y] for t in units for y in years))
    return Built(model, x, budget, out)
