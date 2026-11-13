from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Retrofit:
    rid: str
    ward: str
    cost: int        # $k


def add_ward_rules(model: mathopt.Model, x: dict, retrofits: list[Retrofit],
                   yard_cap: dict[str, int], max_share: float) -> None:
    """Each ward's yard stages at most yard_cap[ward] retrofits; no ward takes more than max_share of the plan."""
    # TODO: the yard rows and the fair-share rows.
    return None


def build(retrofits: list[Retrofit], budget: int, yard_cap: dict[str, int],
          max_share: float) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="streetlights")
    x = {r.rid: model.add_binary_variable(name=f"x_{r.rid}") for r in retrofits}
    model.add_linear_constraint(sum(r.cost * x[r.rid] for r in retrofits) <= budget, name="budget")
    add_ward_rules(model, x, retrofits, yard_cap, max_share)
    model.maximize(sum(x.values()))
    return model, x


if __name__ == "__main__":
    blocks = [Retrofit("N1", "North", 40), Retrofit("N2", "North", 35), Retrofit("S1", "South", 50)]
    model, x = build(blocks, 200, {"North": 1}, 0.5)
    print(len(list(model.linear_constraints())), "rows")
