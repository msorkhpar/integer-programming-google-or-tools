from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: tuple[int, ...]          # spend in each year of work, start year first ($k)
    value: dict[int, int]          # value if started in that year ($k); its keys are the window


@dataclass
class Plan:
    plan_id: str
    budget: dict[int, int]                                            # year -> $k
    overrides: dict[str, tuple] = field(default_factory=dict)         # pid -> ("start_in", y) or ("out", None)
    parent_id: str | None = None


def solve(plan: Plan, projects: list[Project]) -> dict[str, int]:
    """The best plan as {pid: start year}: at most one start per project, spend within each year's budget."""
    model = mathopt.Model()
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.value}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.value) <= 1)
        kind, year = plan.overrides.get(p.pid, (None, None))
        for t in p.value:
            if kind == "out" or (kind == "start_in" and t != year):
                x[p.pid, t].upper_bound = 0
            if kind == "start_in" and t == year:
                x[p.pid, t].lower_bound = 1
    for y, cap in plan.budget.items():
        spend = mathopt.LinearExpression()
        for p in projects:
            for t in p.value:
                if 0 <= y - t < len(p.cost):
                    spend += p.cost[y - t] * x[p.pid, t]
        model.add_linear_constraint(spend <= cap)
    model.maximize(sum(p.value[t] * x[p.pid, t] for p in projects for t in p.value))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, result.termination
    return {pid: t for (pid, t), v in x.items() if result.variable_values(v) > 0.5}


def copy_with_overrides(base: Plan, plan_id: str, overrides: dict[str, tuple]) -> Plan:
    """A copy of base, sharing no container with it, with the given overrides added on top."""
    return Plan(plan_id, dict(base.budget), {**base.overrides, **overrides}, parent_id=base.plan_id)


def diff(a: dict[str, int], b: dict[str, int]) -> dict[str, list]:
    """From plan a to plan b: projects selected, deferred, and shifted as (pid, a's year, b's year)."""
    return {"selected": sorted(set(b) - set(a)),
            "deferred": sorted(set(a) - set(b)),
            "shifted": [(p, a[p], b[p]) for p in sorted(set(a) & set(b)) if a[p] != b[p]]}


def what_if(base: Plan, plan_id: str, overrides: dict[str, tuple], projects: list[Project]) -> tuple[Plan, dict]:
    """Copy base, override, re-optimize both, and diff the two plans."""
    trial = copy_with_overrides(base, plan_id, overrides)
    return trial, diff(solve(base, projects), solve(trial, projects))


if __name__ == "__main__":
    mains = [Project("M-1", (300,), {2027: 500, 2028: 450}), Project("M-2", (400,), {2027: 420, 2028: 400})]
    base = Plan("W-1", {2027: 400, 2028: 400})
    print(what_if(base, "W-2", {"M-1": ("start_in", 2028)}, mains))
