"""Lesson 13.1.4: a why-deferred report for GridCap medium's best deferred projects.

For the three deferred projects with the highest NPV at their earliest start: the rows that refuse
each start as the plan stands, and the cost of forcing the project in, as an interval because both
solves stop at the run setting's 0.1% gap. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from cipt_diagnose import why_deferred
from cipt_model import build, params, plan_of, solve
from gridcap import generate

if __name__ == "__main__":
    medium = generate("medium")
    b = build(medium)
    base = solve(b.model, params(gap=1e-3))
    plan = plan_of(b, base)
    deferred = sorted((p for p in medium.projects if p.project_id not in plan), key=lambda p: -p.value)[:3]
    print(f"base plan: {len(plan)} projects, NPV {base.objective_value():,.0f}, "
          f"bound {base.termination.objective_bounds.dual_bound:,.0f}")
    for p in deferred:
        d = why_deferred(b, base, p.project_id)
        print()
        print(f"{p.project_id} {p.name}: NPV ${p.value:,}k at {p.earliest_start}, cost {p.cost_profile}")
        for t, rows in d.refused_by.items():
            print(f"  start {t}: refused by {', '.join(rows) if rows else 'nothing'}")
        print(f"  forcing it in costs between ${d.cost_low:,.0f}k and ${d.cost_high:,.0f}k of NPV")
        print(f"  what gives way: {len(d.gives_way)} changes, e.g. {', '.join(d.gives_way[:4])}")
