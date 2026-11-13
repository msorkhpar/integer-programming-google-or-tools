from __future__ import annotations

import math
from dataclasses import dataclass, field

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


def solve(b: Built) -> mathopt.SolveResult:
    """HiGHS to a zero gap."""
    return mathopt.solve(b.model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))


def plan_of(b: Built, result: mathopt.SolveResult) -> dict[str, int]:
    values = result.variable_values()
    return {pid: t for (pid, t), v in sorted(b.x.items()) if values[v] > 0.5}


def check(snapshot: dict, scenario: dict, plan: dict[str, int]) -> list[str]:
    """Every row the plan breaks, by name, from the data alone (milestone 2's checker)."""
    projects, broken = snapshot["projects"], []
    for pid, p in projects.items():
        if p["must"] and pid not in plan:
            broken.append(f"must_{pid}")
    groups: dict[str, int] = {}
    for pid in plan:
        if projects[pid]["group"]:
            groups[projects[pid]["group"]] = groups.get(projects[pid]["group"], 0) + 1
    broken += [f"alt_{g}" for g, n in sorted(groups.items()) if n > 1]
    for pid, t in sorted(plan.items()):
        p = projects[pid]
        if p["parent"] and (p["parent"] not in plan or plan[p["parent"]] + p["lag"] > t):
            broken.append(f"after_{pid}_{t}")
    for y in snapshot["years"]:
        used = sum(spend(projects[pid], t).get(y, 0) for pid, t in plan.items())
        if used > budget(snapshot, scenario, y):
            broken.append(f"budget_{y}")
        for r, limits in sorted(snapshot["region_budget"].items()):
            if sum(spend(projects[pid], t).get(y, 0) for pid, t in plan.items() if projects[pid]["region"] == r) > limits[y]:
                broken.append(f"region_{r}_{y}")
        for g in sorted(snapshot["crews"]):
            if sum(projects[pid]["crews"] for pid, t in plan.items()
                   if projects[pid]["program"] == g and y in spend(projects[pid], t)) > crews(snapshot, scenario, g, y):
                broken.append(f"crews_{g}_{y}")
    for r, floor in sorted(snapshot["floor"].items()):
        if sum(sum(projects[pid]["cost"]) for pid in plan if projects[pid]["region"] == r) < floor:
            broken.append(f"floor_{r}")
    return broken


# --- Yours: why a project was deferred --------------------------------------------------------------


def refused_by(snapshot: dict, scenario: dict, plan: dict[str, int], pid: str) -> dict[int, list[str]]:
    """For each start year of a deferred project: the rows the plan breaks if it is added there."""
    return {t: check(snapshot, scenario, {**plan, pid: t}) for t in starts(snapshot["projects"][pid])}


@dataclass
class Forced:
    cost: float                      # NPV given up to fund the project, $k
    gives_way: list[str]             # "J2 dropped", "J3 2027->2028", by project id


def forcing_cost(snapshot: dict, scenario: dict, pid: str) -> Forced | None:
    """What the best plan loses when `pid` must be funded; None when no plan funds it."""
    base_model = build(snapshot, scenario)
    base = solve(base_model)
    forced_model = build(snapshot, {**scenario, "force_in": [*scenario.get("force_in", []), pid]})
    forced = solve(forced_model)
    if forced.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    before, after = plan_of(base_model, base), plan_of(forced_model, forced)
    gives = [f"{i} dropped" if i not in after else f"{i} {before[i]}->{after[i]}"
             for i in sorted(before) if after.get(i) != before[i]]
    return Forced(base.objective_value() - forced.objective_value(), gives)


def cost_interval(base_primal: float, base_bound: float, forced_primal: float,
                  forced_bound: float) -> tuple[float, float]:
    """The forcing cost when both solves stop at a gap: it lies between these two numbers."""
    return max(0.0, base_primal - forced_bound), base_bound - forced_primal
