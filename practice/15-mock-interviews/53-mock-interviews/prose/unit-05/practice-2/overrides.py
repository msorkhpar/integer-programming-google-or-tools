from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]


def start_variables(model: mathopt.Model, projects: list[Project]) -> dict:
    """Given: x[(pid, year)] for every allowed start year, and each project starts at most once."""
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    return x


def apply_overrides(model: mathopt.Model, x: dict, projects: list[Project], overrides: list[tuple]) -> None:
    """Each override is ("start_in", pid, year), ("never", pid), ("not_before", pid, year) or ("fund", pid)."""
    # TODO: turn each override into bounds, or a row where no bound can say it.
    return None


def build(projects: list[Project], overrides: list[tuple]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="overrides")
    x = start_variables(model, projects)
    apply_overrides(model, x, projects, overrides)
    return model, x


if __name__ == "__main__":
    model, x = build([Project("P1", (2027, 2028))], [("not_before", "P1", 2028)])
    print({k: (v.lower_bound, v.upper_bound) for k, v in x.items()})
