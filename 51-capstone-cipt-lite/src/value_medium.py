"""Lesson 13.1.3: GridCap medium's three coefficient tables, and the plans they lead to.

Prints the NPV table rebuilt from cash flows against GridCap's own, one asset's risk reduction with
and without its RUL as the anchor, one project's weighted value, a digest of each table, and the
plan each objective chooses under the same rules. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import hashlib
import json

from ortools.math_opt.python import mathopt

from cipt_model import build, params, plan_of, solve
from cipt_value import (REFERENCE, benefit_forecast, eta_from_rul, npv_table, risk_table, value_table,
                        weights)


def table_digest(table: dict) -> str:
    """sha256 of a table with every value rounded to 3 decimals: what a test pins."""
    rows = sorted([pid, t, round(v, 3)] for (pid, t), v in table.items())
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode("ascii")).hexdigest()[:12]


def row(label: str, table: dict, pid: str, years, fmt: str) -> None:
    print(f"  {label:<26}" + "".join(f"{format(table[pid, t], fmt):>10}" for t in years))


if __name__ == "__main__":
    medium, forecast = benefit_forecast("medium")
    npv = npv_table(medium, forecast)
    same = sum(npv[p.project_id, t] == p.npv[t] for p in medium.projects for t in p.starts())
    print(f"NPV table: {len(npv)} entries, {same} equal to GridCap's own table")
    p = medium.project("P086")
    ratio, decay = forecast["P086"]
    print(f"P086 {p.name}: costs {p.cost_profile}, benefit ratio {ratio:.3f}, decay {decay:.3f}")
    print(f"  {'start year':<26}" + "".join(f"{t:>10}" for t in p.starts()))
    row("NPV ($k)", npv, "P086", p.starts(), ",")

    rr, catalog = risk_table(medium), risk_table(medium, anchor_rul=False)
    a = medium.asset(p.asset_id)
    print()
    print(f"asset {a.asset_id}: age {a.age}, beta {a.weibull_beta}, catalog eta {a.weibull_eta}, RUL {a.rul}, "
          f"CoF ${a.cof:,}k; eta that makes the RUL the median: {eta_from_rul(a.age, a.rul, a.weibull_beta):.1f}")
    row("risk removed, catalog eta", catalog, "P086", p.starts(), ",.1f")
    row("risk removed, RUL-anchored", rr, "P086", p.starts(), ",.1f")

    value = value_table(npv, rr)
    w = weights()
    print()
    print(f"weights from ratings: npv {w['npv']:.3f}, risk {w['risk']:.3f}; "
          f"references: npv ${REFERENCE['npv']:,.0f}k, risk ${REFERENCE['risk']:,.0f}k")
    row("value (points)", value, "P086", p.starts(), ".3f")
    print(f"table digests: npv {table_digest(npv)}, risk {table_digest(rr)}, value {table_digest(value)}")

    print()
    b = build(medium)
    print(f"{'objective':<10} {'projects':>9} {'NPV ($k)':>10} {'risk removed ($k)':>18}")
    for name, coefficient in (("npv", npv), ("value", value), ("risk", rr)):
        b.model.maximize(mathopt.fast_sum(coefficient[key] * x for key, x in b.x.items()))
        plan = plan_of(b, solve(b.model, params(gap=1e-3)))
        print(f"{name:<10} {len(plan):>9} {sum(npv[k] for k in plan.items()):>10,} "
              f"{sum(rr[k] for k in plan.items()):>18,.0f}")
