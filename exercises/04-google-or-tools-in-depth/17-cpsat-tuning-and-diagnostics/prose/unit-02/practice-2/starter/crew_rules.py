from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Rule:
    name: str
    terms: dict[str, int]       # variable name -> coefficient
    sense: str                  # "<=" or ">="
    rhs: int


def add_rule(model: cp_model.CpModel, var: dict[str, cp_model.IntVar], rule: Rule):
    """Given: add one rule as a linear constraint and return it."""
    expr = sum(coef * var[name] for name, coef in rule.terms.items())
    return model.add(expr <= rule.rhs) if rule.sense == "<=" else model.add(expr >= rule.rhs)


def clashing_rules(variables: dict[str, tuple[int, int]], rules: list[Rule]) -> list[str]:
    """Names of a set of rules that cannot hold together, as CP-SAT reports it; [] if all can."""
    # TODO: one flag per rule, assume every flag, solve with one worker, map indices to names.
    return []


if __name__ == "__main__":
    crews = {"north": (2, 6), "south": (1, 6)}
    print(clashing_rules(crews, [Rule("pair_cap", {"north": 1, "south": 1}, "<=", 2)]))
