from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]          # the years it may start in
    must_do: bool = False


def start_variables(model: mathopt.Model, projects: list[Project]) -> dict:
    """x[(pid, year)] = 1 when the project starts in that year; only years in its window exist."""
    return {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}


def add_start_rules(model: mathopt.Model, x: dict, projects: list[Project]) -> None:
    """Given: each project starts at most once, and each must-do exactly once."""
    for p in projects:
        started = sum(x[p.pid, t] for t in p.starts)
        if p.must_do:
            model.add_linear_constraint(started == 1, name=f"must_{p.pid}")
        else:
            model.add_linear_constraint(started <= 1, name=f"once_{p.pid}")


def add_outage_rules(model: mathopt.Model, x: dict, projects: list[Project],
                     max_starts: dict[int, int], coordinated: list[tuple[str, str]]) -> None:
    """At most max_starts[year] starts per year; each coordinated pair together, in one year, or not at all."""
    for year, cap in max_starts.items():
        starting = [x[p.pid, year] for p in projects if (p.pid, year) in x]
        if starting:
            model.add_linear_constraint(sum(starting) <= cap, name=f"crews_{year}")

    def at(pid: str, year: int):
        return x[pid, year] if (pid, year) in x else 0

    by_id = {p.pid: p for p in projects}
    for a, b in coordinated:
        years = sorted(set(by_id[a].starts) | set(by_id[b].starts))
        for t in years:
            model.add_linear_constraint(at(a, t) - at(b, t) == 0, name=f"together_{a}_{b}_{t}")


def build(projects: list[Project], max_starts: dict[int, int],
          coordinated: list[tuple[str, str]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="feeder-upgrades")
    x = start_variables(model, projects)
    add_start_rules(model, x, projects)
    add_outage_rules(model, x, projects, max_starts, coordinated)
    return model, x


if __name__ == "__main__":
    feeders = [Project("F1", (2027, 2028), must_do=True), Project("F2", (2027, 2028)), Project("F3", (2028,))]
    model, x = build(feeders, {2027: 1, 2028: 2}, [("F2", "F3")])
    print(len(list(model.linear_constraints())), "rows")
