from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost_profile: tuple[int, ...]     # spend in each year of work, start year first
    starts: tuple[int, ...]           # the years it may start in


def start_variables(model: mathopt.Model, projects: list[Project]) -> dict:
    return {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}


def yearly_spend(projects: list[Project], x: dict, years: list[int]) -> dict:
    """{year: what the plan spends that year}, as linear expressions in the start variables."""
    spend = {y: mathopt.LinearExpression() for y in years}
    for p in projects:
        for t in p.starts:
            for k, c in enumerate(p.cost_profile):
                if t + k in spend:
                    spend[t + k] += c * x[p.pid, t]
    return spend


def add_steady_spend(model: mathopt.Model, spend: dict, years: list[int], max_step: int) -> None:
    """From each year of the plan to the next, total spend rises or falls by at most `max_step`."""
    for before, after in zip(years, years[1:]):
        model.add_linear_constraint(spend[after] - spend[before] <= max_step, name=f"rise_{after}")
        model.add_linear_constraint(spend[before] - spend[after] <= max_step, name=f"fall_{after}")


def allowed(projects: list[Project], years: list[int], max_step: int, schedule: dict[str, int]) -> bool:
    """Fix the schedule {pid: start year} (every other start variable at 0) and ask whether it is allowed."""
    model = mathopt.Model(name="steady")
    x = start_variables(model, projects)
    for (pid, t), var in x.items():
        value = 1.0 if schedule.get(pid) == t else 0.0
        var.lower_bound = value
        var.upper_bound = value
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    add_steady_spend(model, yearly_spend(projects, x, years), years, max_step)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


if __name__ == "__main__":
    mains = [Project("M1", (100, 100), (2027, 2028))]
    print(allowed(mains, [2027, 2028, 2029], 150, {"M1": 2027}))
