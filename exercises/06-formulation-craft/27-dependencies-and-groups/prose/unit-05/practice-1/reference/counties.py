from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    county: str
    cost: tuple[int, ...]
    starts: tuple[int, ...]


def add_county_rules(model: mathopt.Model, x: dict, projects: list[Project], years: tuple[int, ...],
                     floor: dict[str, int], cap: dict[str, int], yearly_cap: dict[tuple[str, int], int]) -> None:
    """Each county's minimum and cap over the plan, and its caps in single years."""
    def in_year(county: str, year: int):
        return sum(p.cost[year - t] * x[p.pid, t] for p in projects if p.county == county
                   for t in p.starts if 0 <= year - t < len(p.cost))

    def whole_plan(county: str):
        return sum(sum(p.cost) * x[p.pid, t] for p in projects if p.county == county for t in p.starts)

    for county, least in floor.items():
        model.add_linear_constraint(whole_plan(county) >= least, name=f"floor_{county}")
    for county, most in cap.items():
        model.add_linear_constraint(whole_plan(county) <= most, name=f"cap_{county}")
    for (county, year), most in yearly_cap.items():
        model.add_linear_constraint(in_year(county, year) <= most, name=f"cap_{county}_{year}")


def build(projects: list[Project], years: tuple[int, ...], floor: dict[str, int], cap: dict[str, int],
          yearly_cap: dict[tuple[str, int], int]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="counties")
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    add_county_rules(model, x, projects, years, floor, cap, yearly_cap)
    return model, x


if __name__ == "__main__":
    projects = [Project("F1", "Ash", (300, 200), (2027, 2028)), Project("F2", "Ash", (250,), (2027,))]
    model, x = build(projects, (2027, 2028, 2029), {"Ash": 400}, {"Ash": 700}, {("Ash", 2028): 300})
    print(model.get_num_linear_constraints(), "rows")
