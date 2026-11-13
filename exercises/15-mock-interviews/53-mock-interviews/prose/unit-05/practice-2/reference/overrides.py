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
    starts = {p.pid: p.starts for p in projects}
    for override in overrides:
        kind, pid = override[0], override[1]
        if kind == "start_in":
            if override[2] not in starts[pid]:
                raise ValueError(f"{override}: {override[2]} is outside the window of {pid}")
            x[pid, override[2]].lower_bound = 1
        elif kind == "never":
            for t in starts[pid]:
                x[pid, t].upper_bound = 0
        elif kind == "not_before":
            for t in starts[pid]:
                if t < override[2]:
                    x[pid, t].upper_bound = 0
        elif kind == "fund":
            model.add_linear_constraint(sum(x[pid, t] for t in starts[pid]) == 1, name=f"fund_{pid}")
    for var in x.values():
        if var.lower_bound > var.upper_bound:
            raise ValueError(f"overrides contradict each other on {var.name}")


def build(projects: list[Project], overrides: list[tuple]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="overrides")
    x = start_variables(model, projects)
    apply_overrides(model, x, projects, overrides)
    return model, x


if __name__ == "__main__":
    model, x = build([Project("P1", (2027, 2028))], [("not_before", "P1", 2028)])
    print({k: (v.lower_bound, v.upper_bound) for k, v in x.items()})
