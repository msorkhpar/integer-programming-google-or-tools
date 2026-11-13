from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    region: str
    cost_profile: tuple[int, ...]     # spend in each year of work, start year first
    starts: tuple[int, ...]           # the years it may start in


def start_variables(model: mathopt.Model, projects: list[Project]) -> dict:
    return {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}


def spend_by_region_year(projects: list[Project], x: dict, years: list[int]) -> dict:
    """{(region, year): what the plan spends in that region in that year}, as linear expressions."""
    regions = sorted({p.region for p in projects})
    spend = {(r, y): mathopt.LinearExpression() for r in regions for y in years}
    # TODO: add each project's cost, year by year, to the right (region, year) entry.
    return spend


if __name__ == "__main__":
    fiber = [Project("F1", "North", (100, 300), (2027, 2028))]
    model = mathopt.Model()
    x = start_variables(model, fiber)
    print(spend_by_region_year(fiber, x, [2027, 2028, 2029]))
