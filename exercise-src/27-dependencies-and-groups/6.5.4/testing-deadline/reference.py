from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]


def add_testing_rules(model: mathopt.Model, x: dict, projects: list[Project], years: tuple[int, ...],
                      testing: dict[str, tuple[str, int]]) -> None:
    """Testing never before its station, and started within k years of it inside the plan."""
    by_id = {p.pid: p for p in projects}

    def begun(pid: str, year: int):
        return mathopt.LinearExpression(sum(x[pid, u] for u in by_id[pid].starts if u <= year))

    for test, (station, k) in testing.items():
        for t in by_id[test].starts:
            model.add_linear_constraint(begun(test, t) <= begun(station, t), name=f"not_before_{test}_{t}")
        for t in years:
            model.add_linear_constraint(begun(test, t) >= begun(station, t - k), name=f"deadline_{test}_{t}")


def build(projects: list[Project], years: tuple[int, ...],
          testing: dict[str, tuple[str, int]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="testing")
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    add_testing_rules(model, x, projects, years, testing)
    return model, x


if __name__ == "__main__":
    years = (2027, 2028, 2029)
    projects = [Project("SUB", years), Project("TEST", years)]
    model, x = build(projects, years, {"TEST": ("SUB", 1)})
    print(model.get_num_linear_constraints(), "rows")
