from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Tower:
    tid: str
    county: str


def add_grant_rules(model: mathopt.Model, x: dict, y: dict, towers: list[Tower], need: dict[str, int],
                    already: dict[str, int], crew_limit: dict[str, int],
                    backhaul: dict[str, list[str]]) -> None:
    """Coverage targets counting earlier upgrades, crew limits, and one backhaul per upgraded hub."""
    for county in sorted({t.county for t in towers}):
        upgraded = sum(x[t.tid] for t in towers if t.county == county)
        still_needed = need.get(county, 0) - already.get(county, 0)
        if still_needed > 0:
            model.add_linear_constraint(upgraded >= still_needed, name=f"cover_{county}")
        if county in crew_limit:
            model.add_linear_constraint(upgraded <= crew_limit[county], name=f"crews_{county}")
    for hub, options in backhaul.items():
        model.add_linear_constraint(sum(y[o] for o in options) == x[hub], name=f"backhaul_{hub}")


def build(towers: list[Tower], need: dict[str, int], already: dict[str, int], crew_limit: dict[str, int],
          backhaul: dict[str, list[str]]) -> tuple[mathopt.Model, dict, dict]:
    model = mathopt.Model(name="broadband-grant")
    x = {t.tid: model.add_binary_variable(name=f"x_{t.tid}") for t in towers}
    y = {o: model.add_binary_variable(name=f"y_{o}") for options in backhaul.values() for o in options}
    add_grant_rules(model, x, y, towers, need, already, crew_limit, backhaul)
    model.maximize(sum(x.values()))
    return model, x, y


if __name__ == "__main__":
    towers = [Tower("A1", "Alder"), Tower("A2", "Alder"), Tower("B1", "Birch")]
    model, x, y = build(towers, {"Alder": 1}, {}, {"Alder": 2}, {"A1": ["A1-fiber", "A1-radio"]})
    print(len(list(model.linear_constraints())), "rows")
