"""CIPT Lite, milestone 4: why a scenario has no plan, and why a project was left out of one.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

* `presolve_checks` reads one project, group or region against one limit at a time (lesson 9.1.2).
  Each check is sound: it never refuses a scenario that has a plan.
* `conflict` finds an irreducible set of rule rows with a deletion filter (lesson 9.1.3), whole
  families first and then the rows inside the families that stay (lesson 9.1.5). Rows that only
  describe the decisions (once, alt, after) stay on: the filter asks which *limits* clash.
* `message` turns the conflict into the planners' words, shows the arithmetic, and proposes the
  smallest change to a number the scenario set, checked by a solve (lesson 9.1.6).
* `why_deferred` says which rows refuse a project as the plan stands (lesson 9.3.1) and what forcing
  it in costs, as an interval when the solves stop at a gap (lesson 9.3.2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from itertools import product

from ortools.math_opt.python import mathopt

from cipt_data import Finding
from cipt_model import Built, Scenario, active, budgets, build, check, crew_limits, family, params, plan_of, solve
from gridcap import Portfolio

FILTERED = ("must", "force", "budget", "region", "crews", "floor")       # the limits; the rest stay on
OPTIMAL = mathopt.TerminationReason.OPTIMAL


# --- Pre-solve checks ----------------------------------------------------------------------------

def required(pf: Portfolio, scenario: Scenario) -> dict[str, list[int]]:
    """Each project every plan must fund, with the start years it may use."""
    need = {p.project_id: list(p.starts()) for p in pf.projects
            if p.must_do or p.project_id in scenario.force_in}
    for pid, year in scenario.fix_start.items():
        need[pid] = [year]
    return need


def presolve_checks(pf: Portfolio, scenario: Scenario) -> list[Finding]:
    by_id = {p.project_id: p for p in pf.projects}
    need = required(pf, scenario)
    limit, crews = budgets(pf, scenario), crew_limits(pf, scenario)
    found = []
    for pid, years in sorted(need.items()):
        p = by_id[pid]
        if pid in scenario.force_out or not set(years) <= set(p.starts()):
            found.append(Finding("no-start", "error", pid, "required, but no start year is left to it"))
            continue
        if not any(all(a <= limit[y] for y, a in p.spend(t).items()) for t in years):
            found.append(Finding("alone-over-budget", "error", pid, "no start fits the yearly budgets on its own"))
        if not any(all(p.crew_months <= crews[p.program, y] for y in p.spend(t)) for t in years):
            found.append(Finding("alone-over-crews", "error", pid, f"needs {p.crew_months} crew-months a year"))
    for y in pf.years:
        least = sum(min(by_id[i].spend(t).get(y, 0) for t in ys) for i, ys in need.items())
        if least > limit[y]:
            found.append(Finding("required-over-budget", "error", str(y), f"${least:,}k required, ${limit[y]:,}k"))
    groups: dict[str, list[str]] = {}
    for pid in need:
        if by_id[pid].alt_group:
            groups.setdefault(by_id[pid].alt_group, []).append(pid)
    found += [Finding("required-alternatives", "error", g, ", ".join(sorted(m)))
              for g, m in sorted(groups.items()) if len(m) > 1]
    for r, floor in sorted(pf.region_floor.items()):
        most = sum(p.capex for p in pf.projects if p.region == r and p.project_id not in scenario.force_out)
        if most < floor:
            found.append(Finding("floor-out-of-reach", "error", r, f"at most ${most:,}k, floor ${floor:,}k"))
    return found


# --- A conflict by deletion filter ---------------------------------------------------------------

@dataclass
class Conflict:
    rows: list[str]
    solves: int


def _switch(b: Built, names, on: bool, saved: dict) -> None:
    for n in names:
        row = b.rules[n]
        if on:
            row.lower_bound, row.upper_bound = saved[n]
        else:
            row.lower_bound, row.upper_bound = -math.inf, math.inf


def _feasible(b: Built) -> bool:
    return solve(b.model).termination.reason == OPTIMAL


def conflict(b: Built) -> Conflict:
    """An irreducible infeasible set of limit rows, with every decision row kept on.

    Deletion filter: switch a candidate off; if the model is still infeasible, leave it off for
    good; otherwise switch it back on, since the conflict needs it. Families first, then rows.
    """
    objective = b.model.objective.as_linear_expression()
    b.model.objective.clear()                               # feasibility is all the filter asks
    saved = {n: (r.lower_bound, r.upper_bound) for n, r in b.rules.items()}
    solves = 0
    try:
        families: dict[str, list[str]] = {}
        for n in b.rules:
            if family(n) in FILTERED:
                families.setdefault(family(n), []).append(n)
        kept: list[str] = []
        for fam, names in families.items():
            _switch(b, names, False, saved)
            solves += 1
            if _feasible(b):
                _switch(b, names, True, saved)
                kept += names
        members = list(kept)
        for n in kept:
            _switch(b, [n], False, saved)
            solves += 1
            if _feasible(b):
                _switch(b, [n], True, saved)
            else:
                members.remove(n)
        return Conflict(sorted(members), solves)
    finally:
        _switch(b, list(saved), True, saved)
        b.model.maximize(objective)


# --- The planner message --------------------------------------------------------------------------

def label(pf: Portfolio, pid: str) -> str:
    return f"{pid} {pf.project(pid).name}"


def describe(name: str, pf: Portfolio, sc: Scenario) -> str:
    kind, _, rest = name.partition("_")
    if kind == "must":
        years = " or ".join(str(t) for t in pf.project(rest).starts())
        return f"{label(pf, rest)} is must-do: it has to start in {years}."
    if kind == "force":
        return f"Planners forced {label(pf, rest)} into the plan."
    if kind == "budget":
        y = int(rest)
        if y in sc.budget:
            return f"Finance locked the {y} budget at ${sc.budget[y]:,}k (GridCap's figure: ${pf.budget[y]:,}k)."
        return f"The {y} budget is ${pf.budget[y]:,}k."
    if kind == "crews":
        program, y = rest.rsplit("_", 1)
        key = (program, int(y))
        if key in sc.crews:
            return (f"{program.capitalize()} crews have {sc.crews[key]} crew-months in {y} in this scenario "
                    f"(GridCap's figure: {pf.crews[key]}).")
        return f"{program.capitalize()} crews have {pf.crews[key]} crew-months in {y}."
    if kind == "region":
        region, y = rest.rsplit("_", 1)
        return f"The {region} region may spend at most ${pf.region_budget[region, int(y)]:,}k in {y}."
    if kind == "floor":
        return f"The {rest} region must receive at least ${pf.region_floor[rest]:,}k over the plan."
    return name


def arithmetic(conflict_rows: list[str], pf: Portfolio, sc: Scenario) -> list[str]:
    """Every start-year combination of the conflict's required projects, and where it runs out."""
    need = required(pf, sc)
    pids = [n.partition("_")[2] for n in conflict_rows if family(n) in ("must", "force")]
    limits = [n for n in conflict_rows if family(n) in ("budget", "crews")]
    out = []
    for years in product(*(need[pid] for pid in pids)):
        chosen = dict(zip(pids, years))
        for n in limits:
            kind, _, rest = n.partition("_")
            if kind == "budget":
                y, cap = int(rest), budgets(pf, sc)[int(rest)]
                use = sum(pf.project(i).spend(t).get(y, 0) for i, t in chosen.items())
                unit = "$k"
            else:
                program, y = rest.rsplit("_", 1)
                y, cap = int(y), crew_limits(pf, sc)[program, int(y)]
                use = sum(pf.project(i).crew_months for i, t in chosen.items()
                          if pf.project(i).program == program and active(pf.project(i), t, y))
                unit = "crew-months"
            if use > cap:
                starts = ", ".join(f"{i} in {t}" for i, t in chosen.items())
                out.append(f"{starts}: {n} needs {use:,} {unit}, has {cap:,}.")
                break
    return out


def repair(b: Built, conflict_rows: list[str]) -> str | None:
    """The smallest raise of one number the scenario set that gives the scenario a plan."""
    pf, sc = b.portfolio, b.scenario
    for n in conflict_rows:
        kind, _, rest = n.partition("_")
        if kind == "crews":
            program, y = rest.rsplit("_", 1)
            key = (program, int(y))
            if key in sc.crews:
                for extra in range(1, 1 + pf.crews[key] - sc.crews[key]):
                    trial = replace(sc, crews={**sc.crews, key: sc.crews[key] + extra})
                    if _feasible(build(pf, trial)):
                        return f"{sc.crews[key] + extra} {program} crew-months in {y} instead of {sc.crews[key]}"
        if kind == "budget" and int(rest) in sc.budget:
            y = int(rest)
            for amount in range(sc.budget[y] + 10, pf.budget[y] + 1, 10):
                if _feasible(build(pf, replace(sc, budget={**sc.budget, y: amount}))):
                    return f"a {y} budget of ${amount:,}k instead of ${sc.budget[y]:,}k"
    return None


def message(b: Built) -> str:
    pf, sc = b.portfolio, b.scenario
    checks = presolve_checks(pf, sc)
    lines = [f"Scenario '{sc.name}' has no plan."]
    if checks:
        lines.append("Pre-solve checks failed:")
        lines += [f"  {f.rule}: {f.subject}: {f.detail}" for f in checks]
        return "\n".join(lines)
    found = conflict(b)
    lines.append("Every pre-solve check passed: no project or limit is impossible on its own.")
    lines.append(f"These {len(found.rows)} rules cannot all hold ({found.solves} solves to find them):")
    lines += [f"  {k}. {describe(n, pf, sc)}" for k, n in enumerate(found.rows, start=1)]
    lines.append("Every way to start the required projects runs out:")
    lines += [f"  {line}" for line in arithmetic(found.rows, pf, sc)]
    fix = repair(b, found.rows)
    if fix:
        lines.append(f"Smallest change that gives the scenario a plan (checked by a solve): {fix}.")
    return "\n".join(lines)


# --- Why deferred ---------------------------------------------------------------------------------

@dataclass
class Deferred:
    pid: str
    refused_by: dict[int, list[str]]            # start year -> rows the plan as it stands breaks
    cost_low: float                              # forcing it in costs at least this ($k of objective)
    cost_high: float                             # and at most this
    gives_way: list[str]                         # projects dropped or moved in the forced plan


def why_deferred(b: Built, base: mathopt.SolveResult, pid: str, gap: float = 1e-3) -> Deferred:
    pf, sc = b.portfolio, b.scenario
    plan = plan_of(b, base)
    refused = {t: check(pf, sc, {**plan, pid: t}) for t in pf.project(pid).starts()}
    fb = build(pf, replace(sc, force_in=sc.force_in | {pid}))
    forced = solve(fb.model, params(gap=gap))
    new = plan_of(fb, forced)
    base_low, base_high = base.objective_value(), base.termination.objective_bounds.dual_bound
    forced_low, forced_high = forced.objective_value(), forced.termination.objective_bounds.dual_bound
    gives = sorted(f"{i} dropped" if i not in new else f"{i} {plan[i]}->{new[i]}"
                   for i in plan if new.get(i) != plan[i])
    return Deferred(pid, refused, max(0.0, base_low - forced_high), base_high - forced_low, gives)
