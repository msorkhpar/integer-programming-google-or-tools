"""Run: the five-year plan for a tiny fleet, made by the fast builder and checked
against the reference builder, and the request scaled for a fleet twice the size.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56. The
request's limits are scaled down to its size and its gap is loose, so the solve is quick. Nothing
is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

import math

from ortools.math_opt.python import mathopt

from renewal.fleet import Transformer, generate_fleet
from renewal.model import build
from renewal.plan import plan
from renewal.reference import build_reference
from renewal.report import outages, spend_by_year
from renewal.request import Plan, Request

UNITS, SEED = 25, 56
REQUEST = Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
                  crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})


def show_plan(fleet: list[Transformer], got: Plan) -> None:
    print(f"{len(got.replace)} units replaced, risk removed ${got.value:,.0f}k ({got.status})")
    taken = outages(fleet, got.replace)
    for y, spend in spend_by_year(fleet, got.replace, REQUEST.outage_cost).items():
        units = sum(1 for year in got.replace.values() if year == y)
        print(f"  {y}: {units} units, {sum(1 for _, t in taken if t == y)} outages, ${spend:,}k")


def rows(m: mathopt.Model) -> dict:
    """Each row's bounds by name, and each coefficient by row and variable name."""
    found: dict = {c.name: (c.lower_bound, c.upper_bound) for c in m.linear_constraints()}
    for e in m.linear_constraint_matrix_entries():
        found[e.linear_constraint.name, e.variable.name] = e.coefficient
    return found


def same_model(a: mathopt.Model, b: mathopt.Model) -> bool:
    """The same variables, rows and coefficients, by name; objective coefficients to 1e-9."""
    oa = {t.variable.name: t.coefficient for t in a.objective.linear_terms()}
    ob = {t.variable.name: t.coefficient for t in b.objective.linear_terms()}
    return ([v.name for v in a.variables()] == [v.name for v in b.variables()] and rows(a) == rows(b)
            and oa.keys() == ob.keys()
            and all(math.isclose(oa[k], ob[k], rel_tol=1e-9, abs_tol=1e-9) for k in oa))


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    fast, slow = build(fleet, REQUEST).model, build_reference(fleet, REQUEST).model
    size = f"{len(list(fast.variables()))} variables, {len(list(fast.linear_constraints()))} rows"
    verdict = "the same" if same_model(fast, slow) else "different"
    print(f"fast builder: {size}; the reference builder's model: {verdict}")
    show_plan(fleet, plan(fleet, REQUEST))
    big = REQUEST.scaled(2)
    print(f"for {2 * UNITS} units: budget ${big.budget:,}k, outages {big.outages}, "
          f"crew-weeks {big.crew_weeks}, spares {big.spares}")

if __name__ == "__main__":
    main()
