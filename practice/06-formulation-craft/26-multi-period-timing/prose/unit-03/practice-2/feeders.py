from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int


def selection_variables(model: mathopt.Model, projects: list[Project], integer: bool = True) -> dict:
    return {p.pid: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.pid}") for p in projects}


def add_aggregated_needs(model, x, parent: str, children: list[str]) -> None:
    """The colleague's version: all the children together, in one row."""
    model.add_linear_constraint(sum(x[c] for c in children) <= len(children) * x[parent])


def add_parent_rows(model, x, parent: str, children: list[str]) -> None:
    """Every child upgrade needs the parent; the parent may be done alone."""
    # TODO: your rows.
    return None


if __name__ == "__main__":
    projects = [Project("SUB", 90, 0), Project("F1", 10, 50), Project("F2", 10, 5)]
    model = mathopt.Model()
    x = selection_variables(model, projects)
    add_parent_rows(model, x, "SUB", ["F1", "F2"])
    print(model.get_num_linear_constraints(), "rows")
