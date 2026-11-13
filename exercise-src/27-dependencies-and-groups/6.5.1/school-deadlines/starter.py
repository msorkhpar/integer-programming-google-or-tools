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
    # TODO: the once rows, the required rows and the access rows.
    return None


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
