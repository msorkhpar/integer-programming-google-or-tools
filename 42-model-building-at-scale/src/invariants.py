"""What every GridCap portfolio must satisfy, checked on GridCap large at ten seeds.

Each invariant is a rule the generator promises whatever the seed: a model builder, a test or a
lesson may rely on it. `violations` returns one line per broken rule, so a passing portfolio gives
an empty list. The last check builds the timing model and confirms that one plan, every must-do at
its earliest start and nothing else, satisfies every row, so the model is feasible. GridCap is
fictional.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from gridcap import Portfolio, generate
from matrix_builder import build_matrix, columns
from tables import tables_of

RULES = ("unique ids", "asset exists", "window inside the horizon", "NPV for every start",
         "parent can come first", "alternatives in pairs", "must-dos fit the yearly budget",
         "must-dos fit the regional caps")


def violations(p: Portfolio) -> list[str]:
    out = []
    by_id = {q.project_id: q for q in p.projects}
    if len(by_id) != len(p.projects):
        out.append("unique ids: two projects share an id")
    assets = {a.asset_id for a in p.assets}
    first, last = p.years[0], p.years[-1]
    groups: dict[str, list] = {}
    for q in p.projects:
        if q.asset_id not in assets:
            out.append(f"asset exists: {q.project_id} works on unknown {q.asset_id}")
        if not first <= q.earliest_start <= q.latest_start or q.latest_start + q.duration - 1 > last:
            out.append(f"window inside the horizon: {q.project_id} {q.earliest_start}-{q.latest_start}, "
                       f"{q.duration} years of work")
        if sorted(q.npv) != list(q.starts()):
            out.append(f"NPV for every start: {q.project_id}")
        if q.parent is not None:
            parent = by_id.get(q.parent)
            if parent is None or parent.earliest_start + q.parent_lag > q.latest_start:
                out.append(f"parent can come first: {q.project_id} after {q.parent}")
        if q.alt_group:
            groups.setdefault(q.alt_group, []).append(q.project_id)
    out += [f"alternatives in pairs: {g} has {len(m)}" for g, m in groups.items() if len(m) != 2]
    year_spend = {y: 0 for y in p.years}
    region_spend: dict[tuple[str, int], int] = {}
    for q in p.projects:
        if q.must_do:
            for y, amount in q.spend(q.earliest_start).items():
                year_spend[y] += amount
                region_spend[(q.region, y)] = region_spend.get((q.region, y), 0) + amount
    out += [f"must-dos fit the yearly budget: {y} needs {s:,} of {p.budget[y]:,}"
            for y, s in year_spend.items() if s > p.budget[y]]
    out += [f"must-dos fit the regional caps: {k} needs {s:,} of {p.region_budget[k]:,}"
            for k, s in region_spend.items() if s > p.region_budget[k]]
    return out


def witness_fits(p: Portfolio) -> bool:
    """Does 'every must-do at its earliest start, nothing else' satisfy every row of the timing model?"""
    tables = tables_of(p)
    proto = build_matrix(tables).export_model()
    cols = columns(tables).merge(tables.projects[["project_id", "must_do", "earliest_start"]], on="project_id")
    x = np.zeros(len(cols))
    x[cols.loc[cols["must_do"] & (cols["start"] == cols["earliest_start"]), "col"]] = 1.0
    m = proto.linear_constraint_matrix
    rows, col, coef = np.array(m.row_ids), np.array(m.column_ids), np.array(m.coefficients)
    activity = np.bincount(rows, weights=coef * x[col], minlength=len(proto.linear_constraints.ids))
    lb, ub = np.array(proto.linear_constraints.lower_bounds), np.array(proto.linear_constraints.upper_bounds)
    return bool(np.all((lb - 1e-9 <= activity) & (activity <= ub + 1e-9)))


if __name__ == "__main__":
    seeds = range(2027, 2037)
    broken, fits, musts = 0, 0, []
    for seed in seeds:
        large = generate("large", seed)
        broken += len(violations(large))
        fits += witness_fits(large)
        musts.append(sum(q.must_do for q in large.projects))
    print(f"GridCap large at {len(seeds)} seeds, {len(RULES)} rules: {broken} violations; "
          f"the must-do plan fits the model at {fits} of {len(seeds)} seeds")
    print(f"must-do projects per seed: {min(musts)} to {max(musts)}")

    large = generate("large")
    must = next(q for q in large.projects if q.must_do)
    heavier = replace(must, cost_profile=(must.cost_profile[0] + large.budget[must.earliest_start],)
                      + must.cost_profile[1:])
    planted = replace(large, projects=tuple(heavier if q is must else q for q in large.projects))
    print(f"\nplanted: {must.project_id} made to cost one whole {must.earliest_start} budget more")
    for line in violations(planted):
        print("  ", line)
    print("   the must-do plan fits the model:", witness_fits(planted))
