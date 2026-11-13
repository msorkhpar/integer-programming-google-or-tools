"""Lesson 13.1.2: the CIPT Lite model on GridCap medium: its size, its plan, and hand-built plans.

The model is solved twice: with the capstone's run setting (a 0.1% relative gap, one HiGHS thread)
and to a zero gap, which gives the reference objective. Then five hand-built plans go to the model
(every start fixed by its bounds) and to the rule checker, which reads only the data. GridCap is a
fictional utility's portfolio.
"""

from __future__ import annotations

from collections import Counter

from cipt_model import allows, build, check, family, npv_of, params, plan_of, solve
from gridcap import generate


def show(label: str, b, plan: dict[str, int]) -> None:
    verdict = "allowed" if allows(b, plan) else "refused"
    broken = check(b.portfolio, b.scenario, plan)
    print(f"{label:<44} model: {verdict:<8} checker: {', '.join(broken) if broken else 'no rule broken'}")


if __name__ == "__main__":
    medium = generate("medium")
    b = build(medium)
    rows = Counter(family(name) for name in b.rules)
    print(f"{len(b.x)} start variables, {len(b.rules)} rows: "
          + ", ".join(f"{k} {v}" for k, v in sorted(rows.items())))

    run = solve(b.model, params(gap=1e-3))
    plan = plan_of(b, run)
    npv, bound = run.objective_value(), run.termination.objective_bounds.dual_bound
    print(f"run setting (gap 0.1%): {run.termination.reason.name}, NPV {npv:,.0f}, bound {bound:,.0f}, "
          f"gap {(bound - npv) / npv:.4%}, {run.solve_stats.node_count:,} nodes, {len(plan)} projects")
    print(f"NPV recomputed from the data: {npv_of(medium, plan):,}; rules broken: {check(medium, b.scenario, plan)}")

    exact = solve(b.model, params(gap=0.0))
    reference = exact.objective_value()
    print(f"zero gap (reference):   {exact.termination.reason.name}, NPV {reference:,.0f}, "
          f"{exact.solve_stats.node_count:,} nodes")
    print(f"run within 0.1% of the reference: {npv >= reference * (1 - 1e-3)} "
          f"({(reference - npv) / reference:.4%} below it)")

    print()
    by_id = {p.project_id: p for p in medium.projects}

    def breaking_only(rule: str, edits):
        """Of the edited plans that break a row of family `rule`, the one that breaks fewest rows."""
        found = []
        for label, edited in edits:
            broken = check(medium, b.scenario, edited)
            if any(family(r) == rule for r in broken):
                found.append((len(broken), label, edited))
                if len(broken) == 1:
                    break
        _, label, edited = min(found, key=lambda f: f[0])
        return label, b, edited

    show("the solver's plan", b, plan)
    show(*breaking_only("must", ((f"{i} (must-do) left out", {k: v for k, v in plan.items() if k != i})
                                 for i in plan if by_id[i].must_do)))
    show(*breaking_only("after", ((f"{c} kept, its parent {by_id[c].parent} left out",
                                   {k: v for k, v in plan.items() if k != by_id[c].parent})
                                  for c in plan if by_id[c].parent)))
    show(*breaking_only("alt", ((f"{p.project_id} added beside its alternative", {**plan, p.project_id: t})
                                for p in medium.projects if p.alt_group and p.project_id not in plan
                                for t in p.starts())))
    show(*breaking_only("budget", ((f"{p.project_id} (${p.capex:,}k) added in {t}", {**plan, p.project_id: t})
                                   for p in medium.projects if p.project_id not in plan for t in p.starts())))
    show(*breaking_only("crews", ((f"{p.project_id} ({p.crew_months} crew-months) added in {t}",
                                   {**plan, p.project_id: t})
                                  for p in medium.projects if p.project_id not in plan for t in p.starts())))
