"""Logic-based Benders on GridCap small: a MILP master picks the plan, CP-SAT checks each outage year."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, generate

from capital import EXACT, build, schedule, solve_highs, value
from outages import SEASONS, jobs, schedulable, minimal_conflict

WEEKS = 52


def master(portfolio: Portfolio, relaxation: str):
    """The plan model plus a relaxation of the outage rule, written in the start variables."""
    cap = build(portfolio)
    outage = jobs(portfolio)
    for y in portfolio.years:
        here = [(pid, j) for pid, j in outage.items() if (pid, y) in cap.x]
        if relaxation in ("year", "season") and here:
            cap.model.add_linear_constraint(
                sum(j.weeks * cap.x[pid, y] for pid, j in here) <= WEEKS, name=f"weeks_{y}")
        if relaxation == "season":
            for s, (first, last) in SEASONS.items():
                inside = [(pid, j) for pid, j in here if first <= j.release and j.deadline <= last]
                if inside and s != "any":
                    cap.model.add_linear_constraint(
                        sum(j.weeks * cap.x[pid, y] for pid, j in inside) <= last - first,
                        name=f"weeks_{y}_{s}")
    return cap


def lbbd(portfolio: Portfolio, *, relaxation: str = "year", strengthen: bool = True, verbose: bool = False):
    cap = master(portfolio, relaxation)
    outage = jobs(portfolio)
    iterations = cuts = 0
    while True:
        iterations += 1
        result = solve_highs(cap.model, EXACT)
        plan = schedule(cap, result)
        new = []
        for y in portfolio.years:
            chosen = [outage[pid] for pid, t in sorted(plan.items()) if t == y and pid in outage]
            if chosen and not schedulable(chosen):
                core = minimal_conflict(chosen) if strengthen else chosen
                new.append((y, [j.project_id for j in core], len(chosen)))
        if verbose:
            told = "; ".join(f"{y}: {'+'.join(ids)} (of {n})" for y, ids, n in new)
            print(f"iter {iterations:2}  master {result.objective_value():9,.1f}  cuts {len(new)}  {told or 'every year schedules'}")
        if not new:
            return result.objective_value(), plan, iterations, cuts
        for y, ids, _ in new:
            # Not all of these outages in year y: at least one of them must start another year or not at all.
            cap.model.add_linear_constraint(sum(cap.x[pid, y] for pid in ids) <= len(ids) - 1,
                                            name=f"nogood_{y}_{cuts}")
            cuts += 1


if __name__ == "__main__":
    small = generate("small")
    best, plan, iterations, cuts = lbbd(small, verbose=True)
    print(f"optimum {best:,.0f}: NPV of the plan {value(small, plan):,}, {iterations} master solves, {cuts} cuts")
    print("relaxation in master   cut from          master solves  cuts")
    for relaxation, label in (("none", "none"), ("year", "52 weeks a year"), ("season", "weeks per season")):
        for strengthen in (False, True):
            if relaxation == "year" and not strengthen:
                continue                                  # 71 master solves; the table needs no more
            best, _, iterations, cuts = lbbd(small, relaxation=relaxation, strengthen=strengthen)
            print(f"{label:22} {'minimal conflict' if strengthen else 'whole year':17} {iterations:13}  {cuts:4}"
                  f"   optimum {best:,.0f}")
