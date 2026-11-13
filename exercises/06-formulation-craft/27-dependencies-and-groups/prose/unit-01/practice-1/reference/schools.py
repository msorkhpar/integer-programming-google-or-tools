from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]


def add_mandates(model: mathopt.Model, x: dict, projects: list[Project], required: dict[str, int],
                 access: dict[str, list[str]], targets: dict[str, tuple[int, int]]) -> None:
    """Each project at most once; required work by its deadline; each school's access target."""
    starts = {p.pid: p.starts for p in projects}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    for pid, deadline in required.items():
        in_time = [x[pid, t] for t in starts[pid] if t <= deadline]
        model.add_linear_constraint(sum(in_time) == 1, name=f"required_{pid}")
    for school, (k, year) in targets.items():
        done_by = [x[pid, t] for pid in access.get(school, []) for t in starts[pid] if t <= year]
        model.add_linear_constraint(sum(done_by) >= k, name=f"access_{school}")


def build(projects: list[Project], required: dict[str, int], access: dict[str, list[str]],
          targets: dict[str, tuple[int, int]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="school-works")
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    add_mandates(model, x, projects, required, access, targets)
    return model, x


if __name__ == "__main__":
    projects = [Project("ROOF", (2027, 2028)), Project("RAMP", (2028, 2029))]
    model, x = build(projects, {"ROOF": 2027}, {"Oak": ["RAMP"]}, {"Oak": (1, 2029)})
    print(model.get_num_linear_constraints(), "rows")
