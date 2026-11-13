from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int        # $k


def add_engineering_rules(model: mathopt.Model, x: dict, needs_any: dict[str, list[str]],
                          all_trigger: list[tuple[list[str], str]], never_with: list[tuple[str, str]],
                          together: list[tuple[str, str]]) -> None:
    """Supports, group triggers, incompatible pairs and pairs funded together, as linear rows."""
    # TODO: one family of rows for each kind of rule.
    return None


def build(projects: list[Project], budget: int, needs_any: dict[str, list[str]],
          all_trigger: list[tuple[list[str], str]], never_with: list[tuple[str, str]],
          together: list[tuple[str, str]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="water-capital")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= budget, name="budget")
    add_engineering_rules(model, x, needs_any, all_trigger, never_with, together)
    model.maximize(sum(x.values()))
    return model, x


if __name__ == "__main__":
    projects = [Project("TX", 900), Project("NM", 400), Project("SM", 350)]
    model, x = build(projects, 2_000, {"TX": ["NM", "SM"]}, [], [], [])
    print(len(list(model.linear_constraints())), "rows")
