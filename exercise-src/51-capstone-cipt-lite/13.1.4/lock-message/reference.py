from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import product

from ortools.math_opt.python import mathopt

# --- Given: the milestone-2 model, with every row named --------------------------------------------


def starts(project: dict) -> list[int]:
    return list(range(project["earliest"], project["latest"] + 1))


def spend(project: dict, start: int) -> dict[int, int]:
    return {start + k: amount for k, amount in enumerate(project["cost"])}


def budget(snapshot: dict, scenario: dict, year: int) -> int:
    return scenario.get("budget", {}).get(year, snapshot["budget"][year])


def crews(snapshot: dict, scenario: dict, program: str, year: int) -> int:
    return scenario.get("crews", {}).get(program, {}).get(year, snapshot["crews"][program][year])


@dataclass
class Built:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    rows: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)


def build(snapshot: dict, scenario: dict) -> Built:
    model = mathopt.Model(name=scenario.get("name", "base"))
    projects = snapshot["projects"]
    x = {(pid, t): model.add_binary_variable(name=f"x_{pid}_{t}") for pid, p in projects.items() for t in starts(p)}
    b = Built(model, x)

    def row(name, expr):
        b.rows[name] = model.add_linear_constraint(expr, name=name)

    def started(pid):
        return mathopt.LinearExpression() + mathopt.fast_sum(x[pid, t] for t in starts(projects[pid]))

    for pid, year in scenario.get("fix_start", {}).items():
        for t in starts(projects[pid]):
            x[pid, t].lower_bound = x[pid, t].upper_bound = 1.0 if t == year else 0.0
    for pid in scenario.get("force_out", []):
        for t in starts(projects[pid]):
            x[pid, t].upper_bound = 0.0
    for pid, p in projects.items():
        row(f"must_{pid}" if p["must"] else f"once_{pid}", started(pid) == 1 if p["must"] else started(pid) <= 1)
    for pid in sorted(scenario.get("force_in", [])):
        row(f"force_{pid}", started(pid) >= 1)
    for g in sorted({p["group"] for p in projects.values() if p["group"]}):
        row(f"alt_{g}", mathopt.fast_sum(started(pid) for pid, p in projects.items() if p["group"] == g) <= 1)
    for c, p in projects.items():
        if p["parent"]:
            parent = projects[p["parent"]]
            for t in starts(p):
                row(f"after_{c}_{t}", mathopt.LinearExpression()
                    + mathopt.fast_sum(x[c, u] for u in starts(p) if u <= t)
                    - mathopt.fast_sum(x[p["parent"], s] for s in starts(parent) if s <= t - p["lag"]) <= 0)
    for y in snapshot["years"]:
        terms = [a * x[pid, t] for pid, p in projects.items() for t in starts(p) for yy, a in spend(p, t).items() if yy == y]
        row(f"budget_{y}", mathopt.LinearExpression() + mathopt.fast_sum(terms) <= budget(snapshot, scenario, y))
        for r, limits in sorted(snapshot["region_budget"].items()):
            terms = [a * x[pid, t] for pid, p in projects.items() if p["region"] == r
                     for t in starts(p) for yy, a in spend(p, t).items() if yy == y]
            row(f"region_{r}_{y}", mathopt.LinearExpression() + mathopt.fast_sum(terms) <= limits[y])
        for g in sorted(snapshot["crews"]):
            terms = [p["crews"] * x[pid, t] for pid, p in projects.items() if p["program"] == g
                     for t in starts(p) if y in spend(p, t)]
            row(f"crews_{g}_{y}", mathopt.LinearExpression() + mathopt.fast_sum(terms) <= crews(snapshot, scenario, g, y))
    for r, floor in sorted(snapshot["floor"].items()):
        row(f"floor_{r}", mathopt.LinearExpression() + mathopt.fast_sum(
            sum(p["cost"]) * x[pid, t] for pid, p in projects.items() if p["region"] == r for t in starts(p)) >= floor)
    model.maximize(mathopt.fast_sum(p["npv"][t] * x[pid, t] for pid, p in projects.items() for t in starts(p)))
    return b


def feasible(b: Built) -> bool:
    """Does the model have a plan? HiGHS on a model with its objective set to 0."""
    objective = b.model.objective.as_linear_expression()
    b.model.objective.clear()
    try:
        return mathopt.solve(b.model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL
    finally:
        b.model.maximize(objective)


def describe(name: str, snapshot: dict, scenario: dict) -> str:
    """One row in the planners' words."""
    kind, _, rest = name.partition("_")
    if kind == "must":
        years = " or ".join(str(t) for t in starts(snapshot["projects"][rest]))
        return f"{rest} (must-do) has to start in {years}."
    if kind == "force":
        return f"{rest} was forced into the plan."
    if kind == "budget":
        set_by = "in this scenario" if int(rest) in scenario.get("budget", {}) else "in the snapshot"
        return f"The {rest} budget is ${budget(snapshot, scenario, int(rest)):,}k {set_by} (snapshot: ${snapshot['budget'][int(rest)]:,}k)."
    if kind == "crews":
        program, year = rest.rsplit("_", 1)
        return (f"{program.capitalize()} crews have {crews(snapshot, scenario, program, int(year))} crew-months in {year} "
                f"(snapshot: {snapshot['crews'][program][int(year)]}).")
    if kind == "region":
        region, year = rest.rsplit("_", 1)
        return f"{region} may spend at most ${snapshot['region_budget'][region][int(year)]:,}k in {year}."
    if kind == "floor":
        return f"{rest} must receive at least ${snapshot['floor'][rest]:,}k."
    return name


# --- Yours: the conflict and the message ------------------------------------------------------------

LIMITS = ("must", "force", "budget", "region", "crews", "floor")


def family(name: str) -> str:
    return name.partition("_")[0]


def conflict(b: Built) -> tuple[list[str], int]:
    """An irreducible set of limit rows that cannot all hold, and the number of solves it took."""
    saved = {n: (r.lower_bound, r.upper_bound) for n, r in b.rows.items()}

    def off(names):
        for n in names:
            b.rows[n].lower_bound, b.rows[n].upper_bound = -math.inf, math.inf

    def on(names):
        for n in names:
            b.rows[n].lower_bound, b.rows[n].upper_bound = saved[n]

    solves, kept = 0, []
    try:
        for fam in LIMITS:
            names = [n for n in b.rows if family(n) == fam]
            if not names:
                continue
            off(names)
            solves += 1
            if feasible(b):
                on(names)
                kept += names
        members = list(kept)
        for n in kept:
            off([n])
            solves += 1
            if feasible(b):
                on([n])
            else:
                members.remove(n)
        return sorted(members), solves
    finally:
        on(saved)


def required(snapshot: dict, scenario: dict, rows: list[str]) -> dict[str, list[int]]:
    """The projects the conflict's must and force rows name, and every project the scenario fixes,
    with the start years left to each."""
    out = {}
    for n in rows:
        if family(n) in ("must", "force"):
            out[n.partition("_")[2]] = starts(snapshot["projects"][n.partition("_")[2]])
    for pid, year in sorted(scenario.get("fix_start", {}).items()):
        out[pid] = [year]
    return out


def arithmetic(snapshot: dict, scenario: dict, rows: list[str]) -> list[str]:
    """For every way to start the conflict's projects, the first of its limits that runs out."""
    need = required(snapshot, scenario, rows)
    lines = []
    for chosen in product(*need.values()):
        plan = dict(zip(need, chosen))
        for n in rows:
            kind, _, rest = n.partition("_")
            if kind == "budget":
                y = int(rest)
                use = sum(spend(snapshot["projects"][pid], t).get(y, 0) for pid, t in plan.items())
                cap, what = budget(snapshot, scenario, y), f"the {y} budget needs ${use:,}k, has $"
            elif kind == "crews":
                g, y = rest.rsplit("_", 1)
                y = int(y)
                use = sum(snapshot["projects"][pid]["crews"] for pid, t in plan.items()
                          if snapshot["projects"][pid]["program"] == g and y in spend(snapshot["projects"][pid], t))
                cap, what = crews(snapshot, scenario, g, y), f"{g} crews in {y} need {use}, have "
            else:
                continue
            if use > cap:
                starts_text = ", ".join(f"{pid} {t}" for pid, t in plan.items())
                lines.append(f"- {starts_text}: {what}{cap:,}{'k' if kind == 'budget' else ''}.")
                break
    return lines


def repair(snapshot: dict, scenario: dict, rows: list[str]) -> str | None:
    """The smallest raise of one number the scenario set that gives the scenario a plan, by solving."""
    for n in rows:
        kind, _, rest = n.partition("_")
        if kind == "crews":
            g, y = rest.rsplit("_", 1)
            y = int(y)
            locked = scenario.get("crews", {}).get(g, {}).get(y)
            if locked is None:
                continue
            for value in range(locked + 1, snapshot["crews"][g][y] + 1):
                trial = {**scenario, "crews": {**scenario["crews"], g: {**scenario["crews"][g], y: value}}}
                if feasible(build(snapshot, trial)):
                    return f"{g} crews in {y} at {value} instead of {locked}"
        if kind == "budget":
            y = int(rest)
            locked = scenario.get("budget", {}).get(y)
            if locked is None:
                continue
            for value in range(locked + 10, snapshot["budget"][y] + 1, 10):
                if feasible(build(snapshot, {**scenario, "budget": {**scenario["budget"], y: value}})):
                    return f"the {y} budget at ${value:,}k instead of ${locked:,}k"
    return None


def message(snapshot: dict, scenario: dict) -> str:
    rows, _ = conflict(build(snapshot, scenario))
    need = required(snapshot, scenario, rows)
    fixed = sorted(scenario.get("fix_start", {}).items())
    lines = [f"Budget Lock '{scenario['name']}' has no plan. These {len(rows) + len(fixed)} rules cannot all hold:"]
    lines += [f"- {describe(n, snapshot, scenario)}" for n in rows]
    lines += [f"- {pid} is fixed by this scenario to start in {year}." for pid, year in fixed]
    lines.append(f"Every way to start {', '.join(need)} runs out:")
    lines += arithmetic(snapshot, scenario, rows)
    fix = repair(snapshot, scenario, rows)
    lines.append(f"Smallest change, checked by a solve: {fix}." if fix else "No single number of the scenario ends it.")
    return "\n".join(lines)
