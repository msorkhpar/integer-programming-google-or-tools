from __future__ import annotations

from ortools.math_opt.python import mathopt


def least_overspend(projects: dict, budget: dict, required: set[str]) -> dict[int, int]:
    """The smallest overspend in each year that lets every required project be funded."""
    # TODO: write the formulation first (variables, elastic budget rows, objective), then build and solve it.
    return {y: 0 for y in budget}


if __name__ == "__main__":
    projects = {"roof": {2027: 300}, "boilers": {2027: 200, 2028: 400}}
    print(least_overspend(projects, {2027: 450, 2028: 450}, {"roof", "boilers"}))
